from pydantic import BaseModel


class TaskCurrentInfo(BaseModel):
    id: int
    name: str
    today_user_id: int | None


class DailyInfoResponse(BaseModel):
    tasks: list[TaskCurrentInfo]
