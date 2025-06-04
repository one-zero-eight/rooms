from typing import Annotated, Iterable

from fastapi import APIRouter, Body
from sqlalchemy import select
from sqlalchemy.sql.functions import count

from src.api.exceptions import (
    TooManyTasksException,
)
from src.api.utils import (
    ROOM_DEPENDENCY,
    check_order_exists,
    check_task_exists,
)
from src.config import SETTINGS_DEPENDENCY
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import Task
from .input_schemas import (
    CreateTaskBody,
    ModifyTaskBody,
    TaskInfoBody,
    RemoveTaskParametersBody,
)
from .output_schemas import (
    TaskListResponse,
    TaskInfo,
    TaskInfoResponse,
)

router = APIRouter(prefix="/task")


@router.post("/create", response_description="The id of the created task")
async def create_task(
    room: ROOM_DEPENDENCY, task: CreateTaskBody, db: DB_SESSION_DEPENDENCY, settings: SETTINGS_DEPENDENCY
) -> int:
    # number_of_tasks = len(room.tasks)
    number_of_tasks: int = await db.scalar(select(count()).where(Task.room_id == room.id))
    if number_of_tasks >= settings.MAX_TASKS:
        raise TooManyTasksException()

    task_obj = Task(name=task.name, description=task.description, start_date=task.start_date, period=task.period)
    task_obj.room_id = room.id
    if task.order_id is not None:
        order = await check_order_exists(task.order_id, room.id, db)
        task_obj.order_id = order.id
    else:
        task_obj.order_id = None
    db.add(task_obj)

    await db.commit()

    return task_obj.id


@router.post("/modify", response_description="True if the operation was successful")
async def modify_task(room: ROOM_DEPENDENCY, task: ModifyTaskBody, db: DB_SESSION_DEPENDENCY) -> bool:
    task_obj = await check_task_exists(task.id, room.id, db)

    for param in ("name", "description", "start_date", "period", "order_id"):
        if (value := getattr(task, param)) is not None:
            if param == "order_id" and value is not None:
                await check_order_exists(value, room.id, db)
            setattr(task_obj, param, value)
    await db.commit()

    return True


@router.post("/remove_parameters", response_description="True if the operation was successful")
async def remove_task_parameters(
    room: ROOM_DEPENDENCY, task: RemoveTaskParametersBody, db: DB_SESSION_DEPENDENCY
) -> bool:
    task_obj = await check_task_exists(task.id, room.id, db)

    for param in ("description", "order_id"):
        if getattr(task, param):
            setattr(task_obj, param, None)
    await db.commit()

    return True


@router.post("/list", response_description="The full list of a room's tasks")
async def get_tasks(room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> TaskListResponse:
    response = TaskListResponse(tasks=[])
    tasks: Iterable[Task] = await db.scalars(select(Task).where(Task.room_id == room.id))
    for task in tasks:
        inactive = task.is_inactive()
        response.tasks.append(TaskInfo(id=task.id, name=task.name, inactive=inactive))

    return response


@router.post("/info", response_description="The task's details")
async def get_task_info(room: ROOM_DEPENDENCY, task: TaskInfoBody, db: DB_SESSION_DEPENDENCY) -> TaskInfoResponse:
    task: Task = await check_task_exists(task.id, room.id, db)
    response = TaskInfoResponse(
        name=task.name,
        description=task.description,
        start_date=task.start_date,
        period=task.period,
        order_id=task.order_id,
        inactive=task.is_inactive(),
    )

    return response


@router.post("/delete", response_description="True if the task was deleted")
async def delete_task(room: ROOM_DEPENDENCY, task_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY) -> bool:
    task: Task = await check_task_exists(task_id, room.id, db)
    await db.delete(task)
    await db.commit()
    return True
