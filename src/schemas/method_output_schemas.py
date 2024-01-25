from pydantic import BaseModel


class TaskDailyInfo(BaseModel):
    id: int
    name: str
    today_user_id: int | None


class DailyInfoResponse(BaseModel):
    tasks: list[TaskDailyInfo]


class IncomingInvitationInfo(BaseModel):
    id: int
    sender: int
    room: int


class IncomingInvitationsResponse(BaseModel):
    invitations: list[IncomingInvitationInfo]


class RoomInfoResponse(BaseModel):
    name: str
    users: list[int]


class Task(BaseModel):
    id: int
    name: str
    inactive: bool


class TaskListResponse(BaseModel):
    tasks: list[Task]
