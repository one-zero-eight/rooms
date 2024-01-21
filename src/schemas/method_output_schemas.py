from pydantic import BaseModel


class TaskCurrentInfo(BaseModel):
    id: int
    name: str
    today_user_id: int | None


class DailyInfoResponse(BaseModel):
    tasks: list[TaskCurrentInfo]


class IncomingInvitationInfo(BaseModel):
    id: int
    sender: int
    room: int


class IncomingInvitationsResponse(BaseModel):
    invitations: list[IncomingInvitationInfo]
