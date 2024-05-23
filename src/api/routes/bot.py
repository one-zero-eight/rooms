from datetime import datetime
from typing import Annotated, Sequence, Iterable

from fastapi import APIRouter, Body
from sqlalchemy import select, exists, delete, update
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
    NotYoursInvitationException,
)
from src.api.utils import (
    check_user_not_exists,
    USER_DEPENDENCY,
    ROOM_DEPENDENCY,
    check_order_exists,
    check_task_exists,
    check_invitation_exists,
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
    TaskInfoBody,
    DeleteInvitationBody,
    RejectInvitationBody,
    OrderInfoBody,
)
from src.schemas.method_output_schemas import (
    DailyInfoResponse,
    TaskDailyInfo,
    IncomingInvitationsResponse,
    IncomingInvitationInfo,
    RoomInfoResponse,
    TaskListResponse,
    Task as TaskInfo,
    TaskInfoResponse,
    SentInvitationsResponse,
    SentInvitationInfo,
    OrderInfoResponse,
    UserInfo,
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
    if user.room_id is not None:
        raise UserHasRoomException()

    room = Room(name=room.name)
    db.add(room)
    await db.flush()
    user.room_id = room.id
    await db.commit()

    return room.id


@bot_router.post("/invitation/create", response_description="The id of created invitation")
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


@bot_router.post("/invitation/accept", response_description="The id of the room the invitation led to")
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

    if invitation.addressee_alias != user.alias:
        raise NotYoursInvitationException()

    user.room_id = invitation.room_id
    await db.delete(invitation)
    await db.commit()

    return invitation.room_id


@bot_router.post("/order/create", response_description="The id of created order")
async def create_order(
    room: ROOM_DEPENDENCY, order: CreateOrderBody, db: DB_SESSION_DEPENDENCY, settings: SETTINGS_DEPENDENCY
) -> int:
    # number_of_orders = len(room.orders)
    number_of_orders: int = await db.scalar(select(count()).where(Order.room_id == room.id))
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
    db.add(order)
    await db.flush()
    for i, user in enumerate(order_list):
        executor = TaskExecutor(user_id=user.id, order_number=i)
        executor.order_id = order.id
        db.add(executor)

    await db.commit()

    return order.id


@bot_router.post("/task/create", response_description="The id of the created task")
async def create_task(
    room: ROOM_DEPENDENCY, task: CreateTaskBody, db: DB_SESSION_DEPENDENCY, settings: SETTINGS_DEPENDENCY
) -> int:
    # number_of_tasks = len(room.tasks)
    number_of_tasks: int = await db.scalar(select(count()).where(Task.room_id == room.id))
    if number_of_tasks >= settings.MAX_TASKS:
        raise TooManyTasksException()

    task_obj = Task(name=task.name, description=task.description, start_date=task.start_date, period=task.period)
    task_obj.room_id = room.id
    if task.order_id is not None:
        order = await check_order_exists(task.order_id, room.id, db)
        task_obj.order_id = order.id
    else:
        task_obj.order_id = None
    db.add(task_obj)

    await db.commit()

    return task_obj.id


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
async def get_daily_info(room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> DailyInfoResponse:
    response = DailyInfoResponse(tasks=[])
    tasks: Iterable[Task] = await db.scalars(select(Task).where(Task.room_id == room.id))
    for task in tasks:
        if task.is_inactive():
            continue

        # executors = task.order.executors
        executors: Sequence[TaskExecutor] = (
            await db.scalars(
                select(TaskExecutor).order_by(TaskExecutor.order_number).where(TaskExecutor.order_id == task.order_id)
            )
        ).all()
        i = (datetime.now() - task.start_date).days % len(executors)

        today_executor: TaskExecutor
        executor: TaskExecutor
        for executor in executors:
            if executor.order_number == i:
                today_executor = executor
                break
        else:
            raise RuntimeError(f"Order number {i} is not found for task_id = {task.id}")

        executor_as_user: User = await db.get_one(User, today_executor.user_id)
        executor_info = UserInfo(alias=executor_as_user.alias, fullname=executor_as_user.fullname)
        response.tasks.append(TaskDailyInfo(id=task.id, name=task.name, today_executor=executor_info))

    return response


@bot_router.post("/invitation/inbox", response_description="A list of the invitations addressed to a user")
async def get_incoming_invitations(user: USER_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> IncomingInvitationsResponse:
    response = IncomingInvitationsResponse(invitations=[])
    if user.alias is None:
        return response

    invitations: Iterable[Invitation] = await db.scalars(
        select(Invitation).where(Invitation.addressee_alias == user.alias)
    )
    for i in invitations:
        if i.expiration_date <= datetime.now():
            await db.delete(i)
            continue
        room_name = (await db.get_one(Room, i.room_id)).name
        sender: User = await db.get_one(User, i.sender_id)
        response.invitations.append(
            IncomingInvitationInfo(
                id=i.id,
                sender=UserInfo(alias=sender.alias, fullname=sender.fullname),
                room=i.room_id,
                room_name=room_name,
            )
        )

    await db.commit()
    return response


@bot_router.post("/room/info", response_description="Info about the user's room")
async def get_room_info(room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> RoomInfoResponse:
    user_ids = [id_ for id_ in await db.scalars(select(User.id).where(User.room_id == room.id))]
    users = [await db.get_one(User, id_) for id_ in user_ids]
    return RoomInfoResponse(
        id=room.id, name=room.name, users=[UserInfo(alias=user.alias, fullname=user.fullname) for user in users]
    )


@bot_router.post("/room/leave", response_description="True if the operation was successful")
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


@bot_router.post("/task/list", response_description="The full list of a room's tasks")
async def get_tasks(room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> TaskListResponse:
    response = TaskListResponse(tasks=[])
    tasks: Iterable[Task] = await db.scalars(select(Task).where(Task.room_id == room.id))
    for task in tasks:
        inactive = task.is_inactive()
        response.tasks.append(TaskInfo(id=task.id, name=task.name, inactive=inactive))

    return response


@bot_router.post("/task/info", response_description="The task's details")
async def get_task_info(room: ROOM_DEPENDENCY, task: TaskInfoBody, db: DB_SESSION_DEPENDENCY) -> TaskInfoResponse:
    task = await check_task_exists(task.id, room.id, db)
    response = TaskInfoResponse(
        name=task.name,
        description=task.description,
        start_date=task.start_date,
        period=task.period,
        order_id=task.order_id,
        inactive=task.is_inactive(),
    )

    return response


@bot_router.post("/invitation/sent", response_description="The list of sent invitations")
async def get_sent_invitations(user: USER_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> SentInvitationsResponse:
    invitations: list[SentInvitationInfo] = []
    i: Invitation
    for i in (await db.execute(select(Invitation).where(Invitation.sender_id == user.id))).unique().scalars():
        if i.expiration_date <= datetime.now():
            await db.delete(i)
            continue
        room_name = (await db.get_one(Room, i.room_id)).name
        invitations.append(
            SentInvitationInfo(id=i.id, addressee=i.addressee_alias, room=i.room_id, room_name=room_name)
        )

    return SentInvitationsResponse(invitations=invitations)


@bot_router.post("/invitation/delete", response_description="True if the invitation was deleted")
async def delete_invitation(user: USER_DEPENDENCY, invitation: DeleteInvitationBody, db: DB_SESSION_DEPENDENCY) -> bool:
    invitation = await check_invitation_exists(invitation.id, user.id, db)
    await db.delete(invitation)
    await db.commit()

    return True


@bot_router.post("/invitation/reject", response_description="True if the invitation was rejected")
async def reject_invitation(user: USER_DEPENDENCY, invitation: RejectInvitationBody, db: DB_SESSION_DEPENDENCY) -> bool:
    invitation = await db.get(Invitation, invitation.id)
    if invitation is None:
        raise InvitationNotExistException()

    if invitation.addressee_alias != user.alias:
        raise NotYoursInvitationException()

    await db.delete(invitation)
    await db.commit()

    return True


@bot_router.post("/order/info", response_description="The information about the order")
async def get_order_info(room: ROOM_DEPENDENCY, order: OrderInfoBody, db: DB_SESSION_DEPENDENCY) -> OrderInfoResponse:
    order = await check_order_exists(order.id, room.id, db)

    users: Iterable[User] = await db.scalars(
        select(User)
        .select_from(TaskExecutor)
        .join(User)
        .order_by(TaskExecutor.order_number)
        .where(TaskExecutor.order_id == order.id)
    )

    return OrderInfoResponse(users=[UserInfo(alias=u.alias, fullname=u.fullname) for u in users])


@bot_router.post("/user/save_alias", response_description="True if the alias was saved")
async def save_user_alias(
    user: USER_DEPENDENCY, db: DB_SESSION_DEPENDENCY, alias: Annotated[str | None, Body()] = None
) -> bool:
    user.alias = alias
    await db.execute(update(Invitation).where(Invitation.addressee_alias == user.alias).values(addressee_alias=alias))
    await db.commit()
    return True


@bot_router.post("/user/save_fullname", response_description="True if the fullname was saved")
async def save_user_fullname(
    user: USER_DEPENDENCY, fullname: Annotated[str, Body()], db: DB_SESSION_DEPENDENCY
) -> bool:
    user.fullname = fullname
    await db.commit()
    return True


@bot_router.post("/task/delete", response_description="True if the task was deleted")
async def delete_task(room: ROOM_DEPENDENCY, task_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY) -> bool:
    task: Task = await check_task_exists(task_id, room.id, db)
    await db.delete(task)
    await db.commit()
    return True


@bot_router.post("/order/delete", response_description="True if the order was deleted")
async def delete_order(room: ROOM_DEPENDENCY, order_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY) -> bool:
    order: Order = await check_order_exists(order_id, room.id, db)
    await db.delete(order)
    await db.commit()
    return True


@bot_router.post("/order/is_in_use", response_description="True if the order is used in some tasks")
async def is_order_in_use(room: ROOM_DEPENDENCY, order_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY) -> bool:
    await check_order_exists(order_id, room.id, db)
    if (await db.execute(select(exists(Task)).where(Task.order_id == order_id))).scalar():
        return True
    return False
