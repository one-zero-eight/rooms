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
