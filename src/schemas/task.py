from datetime import datetime

from src.schemas.utils import MyBaseModel


class BaseTaskSchema(MyBaseModel):
    name: str
    description: str | None = None
    start_date: datetime
    period: int


class CreateTaskSchema(BaseTaskSchema):
    room_id: int


class TaskSchema(BaseTaskSchema):
    id: int
    room_id: int
    order_id: int | None = None


class ModifyTaskSchema(TaskSchema):
    name: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    period: int | None = None
    order_id: int | None = None
