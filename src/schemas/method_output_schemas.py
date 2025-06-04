from pydantic import BaseModel


class UserInfo(BaseModel):
    id: int
    alias: str | None
    fullname: str | None


class TaskDailyInfo(BaseModel):
    id: int
    name: str
    today_executor: UserInfo | None


class DailyInfoResponse(BaseModel):
    tasks: list[TaskDailyInfo]


class IncomingInvitationInfo(BaseModel):
    id: int
    sender: UserInfo
    room: int
    room_name: str


class IncomingInvitationsResponse(BaseModel):
    invitations: list[IncomingInvitationInfo]


class RoomInfoResponse(BaseModel):
    id: int
    name: str
    users: list[UserInfo]


class SentInvitationInfo(BaseModel):
    id: int
    addressee: str
    room: int
    room_name: str


class SentInvitationsResponse(BaseModel):
    invitations: list[SentInvitationInfo]


class OrderInfoResponse(BaseModel):
    users: list[UserInfo]


class ListOfOrdersResponse(BaseModel):
    users: list[UserInfo]
    orders: dict[int, list[int]]


class RuleInfo(BaseModel):
    id: int
    name: str
    text: str
