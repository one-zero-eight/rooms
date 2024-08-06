from typing import Annotated

from fastapi import APIRouter, Body
from sqlalchemy import delete, update, func

from src.api.utils import (
    check_user_not_exists,
    USER_DEPENDENCY,
)
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User, Invitation
from src.schemas.method_input_schemas import (
    CreateUserBody,
)

router = APIRouter(prefix="/user")


@router.post("/create", response_description="The user's id")
async def create_user(user: CreateUserBody, db: DB_SESSION_DEPENDENCY) -> int:
    await check_user_not_exists(user.user_id, db)

    new_user = User(user.user_id)
    db.add(new_user)
    await db.commit()

    return new_user.id


@router.post("/save_alias", response_description="True if the alias was saved")
async def save_user_alias(
    user: USER_DEPENDENCY, db: DB_SESSION_DEPENDENCY, alias: Annotated[str | None, Body()] = None
) -> bool:
    if user.alias is not None:
        if alias is None:
            await db.execute(delete(Invitation).where(func.lower(Invitation.addressee_alias) == user.alias.lower()))
        else:
            await db.execute(
                update(Invitation)
                .where(func.lower(Invitation.addressee_alias) == user.alias.lower())
                .values(addressee_alias=alias)
            )
    user.alias = alias
    await db.commit()
    return True


@router.post("/save_fullname", response_description="True if the fullname was saved")
async def save_user_fullname(
    user: USER_DEPENDENCY, fullname: Annotated[str, Body()], db: DB_SESSION_DEPENDENCY
) -> bool:
    user.fullname = fullname
    await db.commit()
    return True
