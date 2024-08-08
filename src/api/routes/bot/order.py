from typing import Annotated, Iterable

from fastapi import APIRouter, Body
from sqlalchemy import select, exists
from sqlalchemy.sql.functions import count

from src.api.exceptions import (
    TooManyOrdersException,
    SpecifiedUserNotInRoomException,
    SpecifiedUserNotExistException,
)
from src.api.utils import (
    ROOM_DEPENDENCY,
    check_order_exists,
)
from src.config import SETTINGS_DEPENDENCY
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User, TaskExecutor, Order, Task
from src.schemas.method_input_schemas import (
    CreateOrderBody,
    OrderInfoBody,
)
from src.schemas.method_output_schemas import (
    OrderInfoResponse,
    UserInfo,
)

router = APIRouter(prefix="/order")


@router.post("/create", response_description="The id of created order")
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
        executor = TaskExecutor(user_id=user.id, order_id=order.id, order_number=i)
        db.add(executor)

    await db.commit()

    return order.id


@router.post("/info", response_description="The information about the order")
async def get_order_info(room: ROOM_DEPENDENCY, order: OrderInfoBody, db: DB_SESSION_DEPENDENCY) -> OrderInfoResponse:
    order = await check_order_exists(order.id, room.id, db)

    users: Iterable[User] = await db.scalars(
        select(User)
        .select_from(TaskExecutor)
        .join(User)
        .order_by(TaskExecutor.order_number)
        .where(TaskExecutor.order_id == order.id)
    )

    return OrderInfoResponse(users=[UserInfo.model_validate(u, from_attributes=True) for u in users])


@router.post("/delete", response_description="True if the order was deleted")
async def delete_order(room: ROOM_DEPENDENCY, order_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY) -> bool:
    order: Order = await check_order_exists(order_id, room.id, db)
    await db.delete(order)
    await db.commit()
    return True


@router.post("/is_in_use", response_description="True if the order is used in some tasks")
async def is_order_in_use(room: ROOM_DEPENDENCY, order_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY) -> bool:
    await check_order_exists(order_id, room.id, db)
    if (await db.execute(select(exists(Task)).where(Task.order_id == order_id))).scalar():
        return True
    return False
