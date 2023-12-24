from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DbSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserSchema(DbSchema):
    id: int
    room_id: int | None = None
    register_datetime: datetime | None = None


class RoomSchema(DbSchema):
    id: int
    name: str
