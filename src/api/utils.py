from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.models.sql import User, Room


async def check_user_not_exists(user_id: int, db: AsyncSession):
    if (await db.get(User, user_id)) is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user already exists")


async def check_user_exists(user_id: int, db: AsyncSession) -> User:
    if (user := await db.get(User, user_id)) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user does not exist")
    return user


async def check_room_not_exists(room_id: int, db: AsyncSession):
    if (await db.get(Room, room_id)) is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The room already exists")


async def check_room_exists(room_id: int, db: AsyncSession) -> Room:
    if (room := await db.get(Room, room_id)) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The room does not exist")
    return room
