from fastapi import APIRouter, HTTPException
from starlette import status

from src.api.auth.utils import BOT_ACCESS_DEPENDENCY
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User, Room
from src.schemas.user import CreateUserSchema, UserSchema


bot_router = APIRouter(prefix="/bot", dependencies=[BOT_ACCESS_DEPENDENCY])


@bot_router.post("/user/create", response_model=UserSchema)
async def create_user(user: CreateUserSchema, session: DB_SESSION_DEPENDENCY):
    if (await session.get(User, user.telegram_id)) is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user is already registered")
    if user.room_id is not None and (await session.get(Room, user.room_id)) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The room does not exist")

    new_user = User(user.telegram_id)
    session.add(new_user)
    await session.commit()

    if user.room_id is not None:
        new_user.room_id = user.room_id
        await session.commit()

    return new_user
