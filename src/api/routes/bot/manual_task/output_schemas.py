from pydantic import BaseModel

from src.schemas.method_output_schemas import UserInfo


class ManualTaskBriefInfo(BaseModel):
    id: int
    name: str
    inactive: bool


class ManualTaskListResponse(BaseModel):
    tasks: list[ManualTaskBriefInfo]


class ManualTaskInfoResponse(BaseModel):
    name: str
    description: str | None
    order_id: int | None


class ManualTaskCurrentResponse(BaseModel):
    number: int
    user: UserInfo
