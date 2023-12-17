from datetime import datetime

from pydantic import Field

from src.schemas.utils import MyBaseModel


class BaseUserSchema(MyBaseModel):
    telegram_id: int = Field(ge=0)
    room_id: int | None = None


class CreateUserSchema(BaseUserSchema):
    pass


class UserSchema(BaseUserSchema):
    register_datetime: datetime | None = None
