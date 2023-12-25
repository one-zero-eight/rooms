from datetime import datetime
from typing import Optional

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
    description: Optional[str]
    start_date: datetime
    period: int = Field(gt=0)  # in days
    order_id: Optional[int]
