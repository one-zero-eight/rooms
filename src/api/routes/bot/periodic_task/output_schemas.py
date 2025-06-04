from datetime import datetime

from pydantic import BaseModel

from src.schemas.method_output_schemas import TaskCurrent


class TaskInfo(BaseModel):
    id: int
    name: str
    inactive: bool


class TaskListResponse(BaseModel):
    tasks: list[TaskInfo]


class TaskInfoResponse(BaseModel):
    name: str
    description: str | None
    start_date: datetime
    period: int
    order_id: int | None
    inactive: bool


class TaskCurrentResponse(BaseModel):
    current: TaskCurrent | None
