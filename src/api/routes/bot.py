from fastapi import APIRouter, HTTPException
from sqlalchemy import select, exists
from sqlalchemy.sql.functions import count
from starlette import status

from src.api.auth.utils import BOT_ACCESS_DEPENDENCY
from src.api.utils import check_room_exists, check_user_not_exists, USER_DEPENDENCY, ROOM_DEPENDENCY
from src.config import SETTINGS_DEPENDENCY
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User, Room, Invitation
from src.schemas.db_schemas import UserSchema, RoomSchema
from src.schemas.method_input_schemas import CreateUserBody, CreateRoomBody, InvitePersonBody

bot_router = APIRouter(prefix="/bot", dependencies=[BOT_ACCESS_DEPENDENCY])


@bot_router.post("/user/create", response_model=UserSchema)
async def create_user(user: CreateUserBody, db: DB_SESSION_DEPENDENCY):
    await check_user_not_exists(user.user_id, db)
    if user.room_id is not None:
        await check_room_exists(user.room_id, db)

    new_user = User(user.user_id)
    db.add(new_user)
    await db.commit()

    if user.room_id is not None:
        new_user.room_id = user.room_id
        await db.commit()

    return new_user


@bot_router.post("/room/create", response_model=RoomSchema)
async def create_room(user: USER_DEPENDENCY, room: CreateRoomBody, db: DB_SESSION_DEPENDENCY):
    if user.room is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The user already has a room")

    room = Room(name=room.name)
    user.room = room
    db.add(room)
    await db.commit()

    return room


@bot_router.post("/user/invite")
async def invite_person(
    user: USER_DEPENDENCY,
    room: ROOM_DEPENDENCY,
    addressee: InvitePersonBody,
    db: DB_SESSION_DEPENDENCY,
    settings: SETTINGS_DEPENDENCY,
):
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

    return True
