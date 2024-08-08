from pydantic import BaseModel

from src.schemas.method_output_schemas import UserInfo


class ManualTaskInfo(BaseModel):
    id: int
    name: str


class ManualTaskListResponse(BaseModel):
    tasks: list[ManualTaskInfo]


class ManualTaskInfoResponse(BaseModel):
    name: str
    description: str | None
    order_id: int | None


class ManualTaskCurrentResponse(BaseModel):
    number: int
    user: UserInfo
