from typing import Annotated, Iterable

from fastapi import APIRouter, Body
from sqlalchemy import select
from sqlalchemy.sql.functions import count

from src.api.exceptions import (
    TooManyTasksException,
    ManualTaskIsInactiveException,
)
from src.api.utils import (
    ROOM_DEPENDENCY,
    check_order_exists,
    check_manual_task_exists,
)
from src.config import SETTINGS_DEPENDENCY
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import ManualTask, TaskExecutor, User
from src.schemas.method_output_schemas import UserInfo
from .input_schemas import (
    CreateManualTaskBody,
    ModifyManualTaskBody,
    RemoveManualTaskParametersBody,
)
from .output_schemas import (
    ManualTaskListResponse,
    ManualTaskBriefInfo,
    ManualTaskInfoResponse,
    ManualTaskCurrentResponse,
)

router = APIRouter(prefix="/manual_task")


@router.post("/create", response_description="The id of the created task")
async def create_manual_task(
    room: ROOM_DEPENDENCY, task: CreateManualTaskBody, db: DB_SESSION_DEPENDENCY, settings: SETTINGS_DEPENDENCY
) -> int:
    # number_of_tasks = len(room.tasks)
    number_of_tasks: int = await db.scalar(select(count()).where(ManualTask.room_id == room.id))
    if number_of_tasks >= settings.MAX_TASKS:
        raise TooManyTasksException()

    task_obj = ManualTask(name=task.name, description=task.description, room_id=room.id)
    if task.order_id is not None:
        order = await check_order_exists(task.order_id, room.id, db)
        task_obj.order_id = order.id
    db.add(task_obj)

    await db.commit()

    return task_obj.id


@router.post("/modify")
async def modify_manual_task(room: ROOM_DEPENDENCY, task: ModifyManualTaskBody, db: DB_SESSION_DEPENDENCY) -> None:
    task_obj = await check_manual_task_exists(task.id, room.id, db)

    for param in ("name", "description", "order_id"):
        if (value := getattr(task, param)) is not None:
            if param == "order_id":
                await check_order_exists(value, room.id, db)
                task_obj.counter = 0
            setattr(task_obj, param, value)
    await db.commit()


@router.post("/remove_parameters")
async def remove_manual_task_parameters(
    room: ROOM_DEPENDENCY, task: RemoveManualTaskParametersBody, db: DB_SESSION_DEPENDENCY
) -> None:
    task_obj = await check_manual_task_exists(task.id, room.id, db)

    for param in ("description", "order_id"):
        if getattr(task, param):
            setattr(task_obj, param, None)
    await db.commit()


@router.post("/list", response_description="The full list of a room's tasks")
async def get_manual_tasks(room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> ManualTaskListResponse:
    response = ManualTaskListResponse(tasks=[])
    tasks: Iterable[ManualTask] = await db.scalars(select(ManualTask).where(ManualTask.room_id == room.id))
    for task in tasks:
        response.tasks.append(ManualTaskBriefInfo(id=task.id, name=task.name, inactive=task.order_id is None))

    return response


@router.post("/info", response_description="The task's details")
async def get_manual_task_info(
    room: ROOM_DEPENDENCY, task_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY
) -> ManualTaskInfoResponse:
    task = await check_manual_task_exists(task_id, room.id, db)
    response = ManualTaskInfoResponse(
        name=task.name,
        description=task.description,
        order_id=task.order_id,
    )

    return response


@router.post("/delete")
async def delete_manual_task(room: ROOM_DEPENDENCY, task_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY) -> None:
    task: ManualTask = await check_manual_task_exists(task_id, room.id, db)
    await db.delete(task)
    await db.commit()


@router.post("/do")
async def do_manual_task(room: ROOM_DEPENDENCY, task_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY) -> None:
    task: ManualTask = await check_manual_task_exists(task_id, room.id, db)
    if task.order_id is None:
        raise ManualTaskIsInactiveException()
    executor_count = await db.scalar(select(count()).where(TaskExecutor.order_id == task.order_id))
    task.counter = (task.counter + 1) % executor_count
    await db.commit()


@router.post("/current_executor")
async def get_current_executor(
    room: ROOM_DEPENDENCY, task_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY
) -> ManualTaskCurrentResponse:
    task: ManualTask = await check_manual_task_exists(task_id, room.id, db)
    executor: TaskExecutor = await db.get_one(TaskExecutor, (task.order_id, task.counter))
    current: User = await db.get_one(User, executor.user_id)
    return ManualTaskCurrentResponse(
        number=task.counter, user=UserInfo(id=current.id, alias=current.alias, fullname=current.fullname)
    )
