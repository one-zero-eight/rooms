from fastapi import APIRouter

from src.api.auth.utils import BOT_ACCESS_DEPENDENCY
from src.api.utils import check_room_exists, check_user_not_exists
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User
from src.schemas.db_schemas import UserSchema
from src.schemas.method_input_schemas import CreateUserBody

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
