from pydantic import BaseModel, Field


class CreateUserBody(BaseModel):
    user_id: int = Field(ge=0)
    room_id: int | None = None


class CreateRoomBody(BaseModel):
    name: str
