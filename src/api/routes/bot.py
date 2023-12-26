from fastapi import APIRouter, HTTPException
from sqlalchemy import select, exists
from sqlalchemy.sql.functions import count
from starlette import status

from src.api.auth.utils import BOT_ACCESS_DEPENDENCY
from src.api.utils import (
    check_user_not_exists,
    USER_DEPENDENCY,
    ROOM_DEPENDENCY,
    check_user_exists,
    check_order_exists,
    check_task_exists,
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
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user already has a room")

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
    addressee_id = addressee.addressee_id
    if (addressee := await db.get(User, addressee_id)) is not None and addressee.room_id is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user already has a room")

    number_of_invitations = (
        await db.execute(select(count()).select_from(Invitation).where(Invitation.sender_id == user.id))
    ).scalar()
    if number_of_invitations >= settings.MAX_INVITATIONS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Maximum number of invitations is reached for the user")

    if (
        await db.execute(
            select(exists(Invitation)).where(Invitation.sender_id == user.id, Invitation.adressee_id == addressee_id)
        )
    ).scalar():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Such an invitation is already sent")

    invite = Invitation(sender_id=user.id, adressee_id=addressee_id, room_id=room.id)
    db.add(invite)
    await db.commit()

    return invite.id


@bot_router.post("/user/accept_invitation", response_description="The id of the room the invitation led to")
async def accept_invitation(user: USER_DEPENDENCY, invitation: AcceptInvitationBody, db: DB_SESSION_DEPENDENCY) -> int:
    if user.room_id is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user already has a room")

    invitation = await db.get(Invitation, invitation.id)
    if invitation is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The invitation is not found")
    if invitation.adressee_id != user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The invitation is not addressed to this user")

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
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Maximum number of orders is reached for the room")

    order_list = []
    for i, user_id in enumerate(order.users):
        order_list.append(user := await check_user_exists(user_id, db))
        if user.room_id != room.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"The user {user_id} does not belong to the room")

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
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Maximum number of tasks is reached for the room")
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
            print(param, value)
            setattr(task_obj, param, value)
    await db.commit()

    return True
