from datetime import datetime
from typing import Sequence, Iterable

from fastapi import APIRouter
from sqlalchemy import select, delete
from sqlalchemy.sql.functions import count

from src.api.exceptions import (
    UserHasRoomException,
)
from src.api.utils import (
    USER_DEPENDENCY,
    ROOM_DEPENDENCY,
)
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User, Room, Invitation, TaskExecutor, Order, Task
from src.schemas.method_input_schemas import (
    CreateRoomBody,
)
from src.schemas.method_output_schemas import (
    DailyInfoResponse,
    TaskDailyInfo,
    RoomInfoResponse,
    UserInfo,
    ListOfOrdersResponse,
)

router = APIRouter(prefix="/room")


@router.post("/create", response_description="The id of created room")
async def create_room(user: USER_DEPENDENCY, room: CreateRoomBody, db: DB_SESSION_DEPENDENCY) -> int:
    if user.room_id is not None:
        raise UserHasRoomException()

    room = Room(name=room.name)
    db.add(room)
    await db.flush()
    user.room_id = room.id
    await db.commit()

    return room.id


@router.post("/daily_info", response_description="Statuses of the tasks of the room")
async def get_daily_info(room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> DailyInfoResponse:
    response = DailyInfoResponse(tasks=[])
    tasks: Iterable[Task] = await db.scalars(select(Task).where(Task.room_id == room.id))
    for task in tasks:
        if task.is_inactive():
            continue
        if not task.is_today_duty(datetime.now()):
            continue

        # executors = task.order.executors
        executors: Sequence[TaskExecutor] = (
            await db.scalars(
                select(TaskExecutor).order_by(TaskExecutor.order_number).where(TaskExecutor.order_id == task.order_id)
            )
        ).all()
        i = task.get_today_executor_index(datetime.now(), len(executors))

        today_executor: TaskExecutor
        executor: TaskExecutor
        for executor in executors:
            if executor.order_number == i:
                today_executor = executor
                break
        else:
            raise RuntimeError(f"Order number {i} is not found for task_id = {task.id}")

        executor_as_user: User = await db.get_one(User, today_executor.user_id)
        executor_info = UserInfo.model_validate(executor_as_user, from_attributes=True)
        response.tasks.append(TaskDailyInfo(id=task.id, name=task.name, today_executor=executor_info))

    return response


@router.post("/info", response_description="Info about the user's room")
async def get_room_info(room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> RoomInfoResponse:
    user_ids = [id_ for id_ in await db.scalars(select(User.id).where(User.room_id == room.id))]
    users = [await db.get_one(User, id_) for id_ in user_ids]
    return RoomInfoResponse(
        id=room.id, name=room.name, users=[UserInfo.model_validate(user, from_attributes=True) for user in users]
    )


@router.post("/leave", response_description="True if the operation was successful")
async def leave_room(user: USER_DEPENDENCY, room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> bool:
    roommates_count = (await db.execute(select(count()).where(User.room_id == room.id))).scalar()
    user.room_id = None
    await db.execute(delete(Invitation).where(Invitation.sender_id == user.id))
    if roommates_count == 1:
        # await db.delete(room)
        # does not work for some reason causing UPDATE invitations SET NULL instead of just cascade deletion
        await db.execute(delete(Room).where(Room.id == room.id))
    await db.commit()
    return True


@router.post("/list_of_orders", response_description="The list of existing orders with info about users")
async def get_list_of_orders(room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> ListOfOrdersResponse:
    orders: Iterable[Order] = await db.scalars(select(Order).where(Order.room_id == room.id))
    response = ListOfOrdersResponse(users=[], orders={})
    user_ids = set()
    for order in orders:
        users: list[int] = list(
            await db.scalars(
                select(User.id)
                .select_from(TaskExecutor)
                .join(User)
                .order_by(TaskExecutor.order_number)
                .where(TaskExecutor.order_id == order.id)
            )
        )
        response.orders[order.id] = users
        user_ids.update(users)

    users: Iterable[User] = await db.scalars(select(User).where(User.id.in_(user_ids)))
    for user in users:
        response.users.append(UserInfo.model_validate(user, from_attributes=True))

    return response
