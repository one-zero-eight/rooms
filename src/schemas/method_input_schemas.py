from datetime import datetime

from pydantic import BaseModel, Field


class CreateUserBody(BaseModel):
    user_id: int = Field(ge=0)


class CreateRoomBody(BaseModel):
    name: str


class InvitePersonBody(BaseModel):
    addressee_id: int


class CreateOrderBody(BaseModel):
    users: list[int]


class AcceptInvitationBody(BaseModel):
    id: int


class CreateTaskBody(BaseModel):
    name: str
    description: str | None = ""
    start_date: datetime
    period: int = Field(gt=0, description="period in days")
    order_id: int | None = None
