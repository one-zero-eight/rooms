from datetime import datetime

from pydantic import BaseModel, Field


class CreateTaskBody(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field("", max_length=1000)
    start_date: datetime
    period: int = Field(gt=0, description="period in days")
    order_id: int | None = None


class ModifyTaskBody(BaseModel):
    id: int
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=3000)
    start_date: datetime | None = None
    period: int | None = Field(None, gt=0, description="period in days")
    order_id: int | None = None


class RemoveTaskParametersBody(BaseModel):
    id: int
    description: bool | None = False
    order_id: bool | None = False


class TaskInfoBody(BaseModel):
    id: int
