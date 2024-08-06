from typing import Annotated

from fastapi import Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import (
    TaskNotExistException,
    OrderNotExistException,
    UserWithoutRoomException,
    RoomNotExistException,
    RoomExistsException,
    UserNotExistException,
    UserExistsException,
    RoomOwningException,
    InvitationNotExistException,
    UserOwningException,
    RuleNotExistException,
)
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User, Room, Order, Task, Invitation, Rule


async def check_user_not_exists(user_id: int, db: AsyncSession):
    if (await db.get(User, user_id)) is not None:
        raise UserExistsException()


async def check_user_exists(user_id: int, db: AsyncSession) -> User:
    if (user := await db.get(User, user_id)) is None:
        raise UserNotExistException()
    # noinspection PyTypeChecker
    return user


async def user_dependency(user_id: Annotated[int, Body(embed=True)], db: DB_SESSION_DEPENDENCY) -> User:
    return await check_user_exists(user_id, db)


USER_DEPENDENCY = Annotated[User, Depends(user_dependency)]


async def check_room_not_exists(room_id: int, db: AsyncSession):
    if (await db.get(Room, room_id)) is not None:
        raise RoomExistsException()


async def check_room_exists(room_id: int, db: AsyncSession) -> Room:
    if (room := await db.get(Room, room_id)) is None:
        raise RoomNotExistException()
    # noinspection PyTypeChecker
    return room


async def room_dependency(user: USER_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> Room:
    if user.room_id is None:
        raise UserWithoutRoomException()
    return await db.get_one(Room, user.room_id)


ROOM_DEPENDENCY = Annotated[Room, Depends(room_dependency)]


async def check_order_exists(order_id: int, room_id: int, db: AsyncSession) -> Order:
    if (order := await db.get(Order, order_id)) is None:
        raise OrderNotExistException()
    if order.room_id != room_id:
        raise RoomOwningException("order")
    # noinspection PyTypeChecker
    return order


async def check_task_exists(task_id: int, room_id: int, db: AsyncSession) -> Task:
    if (task := await db.get(Task, task_id)) is None:
        raise TaskNotExistException()
    if task.room_id != room_id:
        raise RoomOwningException("task")
    # noinspection PyTypeChecker
    return task


async def check_invitation_exists(invitation_id: int, sender_id: int, db: AsyncSession) -> Invitation:
    if (invitation := await db.get(Invitation, invitation_id)) is None:
        raise InvitationNotExistException()
    if invitation.sender_id != sender_id:
        raise UserOwningException("invitation")
    # noinspection PyTypeChecker
    return invitation


async def check_rule_exists(rule_id: int, room_id: int, db: AsyncSession) -> Rule:
    if (rule := await db.get(Rule, rule_id)) is None:
        raise RuleNotExistException()
    if rule.room_id != room_id:
        raise RoomOwningException("rule")
    # noinspection PyTypeChecker
    return rule
