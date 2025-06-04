from pydantic import BaseModel, Field


class CreateUserBody(BaseModel):
    user_id: int = Field(ge=0)


class CreateRoomBody(BaseModel):
    name: str = Field(min_length=1, max_length=250)


class InvitePersonBody(BaseModel):
    alias: str = Field(min_length=1, max_length=32)


class CreateOrderBody(BaseModel):
    users: list[int]


class AcceptInvitationBody(BaseModel):
    id: int


class DeleteInvitationBody(BaseModel):
    id: int


class RejectInvitationBody(BaseModel):
    id: int


class OrderInfoBody(BaseModel):
    id: int


class CreateRuleBody(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=3000)


class EditRuleBody(BaseModel):
    id: int
    name: str | None = Field(None, min_length=1, max_length=100)
    text: str | None = Field(None, min_length=1, max_length=3000)
