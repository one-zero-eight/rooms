from pydantic import BaseModel


class ManualTaskInfo(BaseModel):
    id: int
    name: str


class ManualTaskListResponse(BaseModel):
    tasks: list[ManualTaskInfo]


class ManualTaskInfoResponse(BaseModel):
    name: str
    description: str | None
    order_id: int | None
