from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy import select, exists, delete
from sqlalchemy.sql.functions import count

from src.api.auth.utils import BOT_ACCESS_DEPENDENCY
from src.api.exceptions import (
    UserHasRoomException,
    TooManyInvitationsException,
    InvitationAlreadySentException,
    InvitationNotExistException,
    TooManyOrdersException,
    SpecifiedUserNotInRoomException,
    TooManyTasksException,
    SpecifiedUserNotExistException,
    InvitationExpiredException,
)
from src.api.utils import (
    check_user_not_exists,
    USER_DEPENDENCY,
    ROOM_DEPENDENCY,
    check_order_exists,
    check_task_exists,
    user_dependency,
)
from src.config import SETTINGS_DEPENDENCY
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User, Room, Invitation, TaskExecutor, Order, Task
from src.schemas.method_input_schemas import (
    CreateUserBody,
    CreateRoomBody,
    InvitePersonBody,
    AcceptInvitationBody,
    CreateOrderBody,
    CreateTaskBody,
    ModifyTaskBody,
)
from src.schemas.method_output_schemas import (
    DailyInfoResponse,
    TaskCurrentInfo,
    IncomingInvitationsResponse,
    IncomingInvitationInfo,
    RoomInfoResponse,
)

bot_router = APIRouter(prefix="/bot", dependencies=[BOT_ACCESS_DEPENDENCY])


@bot_router.post("/user/create", response_description="The user's id")
async def create_user(user: CreateUserBody, db: DB_SESSION_DEPENDENCY) -> int:
    await check_user_not_exists(user.user_id, db)

    new_user = User(user.user_id)
    db.add(new_user)
    await db.commit()

    return new_user.id


@bot_router.post("/room/create", response_description="The id of created room")
async def create_room(user: USER_DEPENDENCY, room: CreateRoomBody, db: DB_SESSION_DEPENDENCY) -> int:
    if user.room is not None:
        raise UserHasRoomException()

    room = Room(name=room.name)
    user.room = room
    db.add(room)
    await db.commit()

    return room.id


@bot_router.post("/user/invite", response_description="The id of created invitation")
async def invite_person(
    user: USER_DEPENDENCY,
    room: ROOM_DEPENDENCY,
    addressee: InvitePersonBody,
    db: DB_SESSION_DEPENDENCY,
    settings: SETTINGS_DEPENDENCY,
) -> int:
    number_of_invitations = (
        await db.execute(select(count()).select_from(Invitation).where(Invitation.sender_id == user.id))
    ).scalar()
    if number_of_invitations >= settings.MAX_INVITATIONS:
        raise TooManyInvitationsException()

    if (
        await db.execute(
            select(exists(Invitation)).where(
                Invitation.sender_id == user.id, Invitation.addressee_alias == addressee.alias
            )
        )
    ).scalar():
        raise InvitationAlreadySentException()

    invite = Invitation(sender_id=user.id, addressee_alias=addressee.alias, room_id=room.id)
    db.add(invite)
    await db.commit()

    return invite.id


@bot_router.post("/user/accept_invitation", response_description="The id of the room the invitation led to")
async def accept_invitation(user: USER_DEPENDENCY, invitation: AcceptInvitationBody, db: DB_SESSION_DEPENDENCY) -> int:
    if user.room_id is not None:
        raise UserHasRoomException()

    invitation = await db.get(Invitation, invitation.id)
    if invitation is None:
        raise InvitationNotExistException()
    if invitation.expiration_date <= datetime.now():
        await db.delete(invitation)
        await db.commit()
        raise InvitationExpiredException()
    # if invitation.addressee_alias != user.id:
    #     raise NotYoursInvitationException()

    user.room_id = invitation.room_id
    await db.delete(invitation)
    await db.commit()

    return invitation.room_id


@bot_router.post("/order/create", response_description="The id of created order")
async def create_order(
    room: ROOM_DEPENDENCY, order: CreateOrderBody, db: DB_SESSION_DEPENDENCY, settings: SETTINGS_DEPENDENCY
) -> int:
    number_of_orders = len(room.orders)
    if number_of_orders >= settings.MAX_ORDERS:
        raise TooManyOrdersException()

    order_list = []
    for i, user_id in enumerate(order.users):
        user = await db.get(User, user_id)
        if user is None:
            raise SpecifiedUserNotExistException(user_id)
        order_list.append(user)
        if user.room_id != room.id:
            raise SpecifiedUserNotInRoomException(user_id)

    order = Order(room_id=room.id)
    for i, user in enumerate(order_list):
        executor = TaskExecutor(user_id=user.id, order_number=i)
        executor.order = order

    db.add(order)
    await db.commit()

    return order.id


@bot_router.post("/task/create", response_description="The id of the created task")
async def create_task(
    room: ROOM_DEPENDENCY, task: CreateTaskBody, db: DB_SESSION_DEPENDENCY, settings: SETTINGS_DEPENDENCY
) -> int:
    number_of_tasks = len(room.tasks)
    if number_of_tasks >= settings.MAX_TASKS:
        raise TooManyTasksException()
    order = await check_order_exists(task.order_id, room.id, db)

    task = Task(name=task.name, description=task.description, start_date=task.start_date, period=task.period)
    task.room_id = room.id
    task.order_id = order.id
    db.add(task)

    await db.commit()

    return task.id


@bot_router.post("/task/modify", response_description="True if the operation was successful")
async def modify_task(room: ROOM_DEPENDENCY, task: ModifyTaskBody, db: DB_SESSION_DEPENDENCY) -> bool:
    task_obj = await check_task_exists(task.id, room.id, db)

    for param in ("name", "description", "start_date", "period", "order_id"):
        if (value := getattr(task, param)) is not None:
            if param == "order_id" and value is not None:
                await check_order_exists(value, room.id, db)
            setattr(task_obj, param, value)
    await db.commit()

    return True


@bot_router.post("/room/daily_info", response_description="Statuses of the tasks of the room")
async def get_daily_info(room: ROOM_DEPENDENCY) -> DailyInfoResponse:
    response = DailyInfoResponse(tasks=[])
    task: Task
    for task in room.tasks:
        if task.order_id is None or task.start_date > datetime.now():
            response.tasks.append(TaskCurrentInfo(id=task.id, name=task.name, today_user_id=None))

        executors = task.order.executors
        i = (datetime.now() - task.start_date).days % len(executors)

        todays_executor: TaskExecutor
        executor: TaskExecutor
        for executor in executors:
            if executor.order_number == i:
                todays_executor = executor
                break

        # noinspection PyUnboundLocalVariable
        response.tasks.append(TaskCurrentInfo(id=task.id, name=task.name, today_user_id=todays_executor.user_id))

    return response


@bot_router.post(
    "/user/incoming_invitations",
    dependencies=[Depends(user_dependency)],
    response_description="A list of the invitations addressed to the user",
)
async def get_incoming_invitations(
    alias: Annotated[str, Body(max_length=64)], db: DB_SESSION_DEPENDENCY
) -> IncomingInvitationsResponse:
    response = IncomingInvitationsResponse(invitations=[])
    i: Invitation
    for i in (await db.execute(select(Invitation).where(Invitation.addressee_alias == alias))).unique().scalars():
        if i.expiration_date <= datetime.now():
            await db.delete(i)
            continue
        response.invitations.append(IncomingInvitationInfo(id=i.id, sender=i.sender_id, room=i.room_id))

    await db.commit()
    return response


@bot_router.post("/room/info", response_description="Info about the user's room")
async def get_room_info(room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> RoomInfoResponse:
    users = [id_ for id_ in (await db.execute(select(User.id).where(User.room_id == room.id))).unique().scalars()]
    return RoomInfoResponse(name=room.name, users=users)


@bot_router.post("/room/leave", response_description="True if the operation was successful")
async def leave_room(user: USER_DEPENDENCY, room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> bool:
    room_users = (await db.execute(select(count()).where(User.room_id == room.id))).scalar()
    user.room_id = None
    await db.commit()
    if room_users == 1:
        # await db.delete(room)
        # does not work for some reason causing UPDATE invitations SET NULL
        await db.execute(delete(Room).where(Room.id == room.id))
    await db.commit()
    return True
