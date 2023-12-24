from typing import Annotated

from fastapi import HTTPException, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User, Room


async def check_user_not_exists(user_id: int, db: AsyncSession):
    if (await db.get(User, user_id)) is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user already exists")


async def check_user_exists(user_id: int, db: AsyncSession) -> User:
    if (user := await db.get(User, user_id)) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user does not exist")
    # noinspection PyTypeChecker
    return user


async def user_dependency(user_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY) -> User:
    return await check_user_exists(user_id, db)


USER_DEPENDENCY = Annotated[User, Depends(user_dependency)]


async def check_room_not_exists(room_id: int, db: AsyncSession):
    if (await db.get(Room, room_id)) is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The room already exists")


async def check_room_exists(room_id: int, db: AsyncSession) -> Room:
    if (room := await db.get(Room, room_id)) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The room does not exist")
    # noinspection PyTypeChecker
    return room


async def room_dependency(user: USER_DEPENDENCY) -> Room:
    if user.room is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user does not have a room")
    # noinspection PyTypeChecker
    return user.room


ROOM_DEPENDENCY = Annotated[Room, Depends(room_dependency)]