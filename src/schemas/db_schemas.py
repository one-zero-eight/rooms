from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DbScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserSchema(DbScheme):
    id: int
    room_id: int | None = None
    register_datetime: datetime | None = None


class RoomSchema(DbScheme):
    id: int
    name: str
