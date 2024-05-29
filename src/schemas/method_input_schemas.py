from datetime import datetime

from pydantic import BaseModel, Field


class CreateUserBody(BaseModel):
    user_id: int = Field(ge=0)


class CreateRoomBody(BaseModel):
    name: str = Field(max_length=250)


class InvitePersonBody(BaseModel):
    alias: str = Field(max_length=32)


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


class RemoveTaskParametersBody(BaseModel):
    id: int
    description: bool | None = False
    order_id: bool | None = False


class TaskInfoBody(BaseModel):
    id: int


class DeleteInvitationBody(BaseModel):
    id: int


class RejectInvitationBody(BaseModel):
    id: int


class OrderInfoBody(BaseModel):
    id: int
