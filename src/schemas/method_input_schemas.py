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
    name: str = Field(max_length=100)
    description: str | None = Field("", max_length=1000)
    start_date: datetime
    period: int = Field(gt=0, description="period in days")
    order_id: int | None = None


class ModifyTaskBody(BaseModel):
    id: int
    name: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=1000)
    start_date: datetime | None = None
    period: int | None = Field(None, gt=0, description="period in days")
    order_id: int | None = None
