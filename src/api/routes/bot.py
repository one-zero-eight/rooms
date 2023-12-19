from fastapi import APIRouter, HTTPException
from starlette import status

from src.api.auth.utils import BOT_ACCESS_DEPENDENCY
from src.api.utils import check_room_exists, check_user_exists, check_user_not_exists
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User, Room
from src.schemas.db_schemas import UserSchema, RoomSchema
from src.schemas.method_input_schemas import CreateUserBody, CreateRoomBody

bot_router = APIRouter(prefix="/bot", dependencies=[BOT_ACCESS_DEPENDENCY])


@bot_router.post("/user/create", response_model=UserSchema)
async def create_user(user: CreateUserBody, db: DB_SESSION_DEPENDENCY):
    await check_user_not_exists(user.telegram_id, db)
    if user.room_id is not None:
        await check_room_exists(user.room_id, db)

    new_user = User(user.telegram_id)
    db.add(new_user)
    await db.commit()

    if user.room_id is not None:
        new_user.room_id = user.room_id
        await db.commit()

    return new_user


@bot_router.post("/room/create", response_model=RoomSchema)
async def create_room(body: CreateRoomBody, db: DB_SESSION_DEPENDENCY):
    user = await check_user_exists(body.user_id, db)
    if user.room is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user already has a room")

    room = Room(name=body.name)
    user.room = room
    db.add(room)
    await db.commit()

    return room
