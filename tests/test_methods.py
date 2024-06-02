from datetime import timedelta, datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import delete, text, exists, select

from src.api.auth.utils import create_jwt
from src.config import get_settings
from src.db_sessions.sqlalchemy_session import session_maker
from src.main import app
from src.models.sql import User, Room, Task, Order, TaskExecutor, Invitation
from src.schemas.method_output_schemas import TaskInfoResponse

client = TestClient(app)

TOKEN = create_jwt({"sub": "tgbot"}, timedelta(minutes=5))


def post(url: str, json: dict) -> Response:
    return client.post(url, json=json, headers={"X-Token": TOKEN})


async def clear_db():
    async with session_maker.get_session() as session:
        for model in (Invitation, TaskExecutor, Order, Task, Room, User):
            await session.execute(delete(model))
            await session.commit()


@pytest_asyncio.fixture(autouse=True)
async def setup_data_in_db():
    async with session_maker.get_session() as session:
        # IMPORTANT: be careful with default autoincrement and fixed IDs
        # this file currently sets all ids from code
        # a test's ids start from 1000
        session.add(Room(1, "room1"))
        session.add(Room(2, "room2"))
        await session.flush()

        session.add(User(1, 1, "alias1", "name1"))
        session.add(User(2, 1, None, "full name2"))
        session.add(User(3, alias="alias3"))
        session.add(User(4, 2))
        session.add(User(5))
        await session.flush()

        session.add(Invitation(1, 1, "alias3", 1))
        session.add(Invitation(2, 1, "alias4", 2))

        session.add(Order(1, 1))
        session.add(Order(2, 2))
        session.add(Order(3, 2))
        await session.flush()

        session.add(TaskExecutor(2, 1, 0))
        session.add(TaskExecutor(1, 1, 1))
        session.add(Task(1, "task1", "bla-bla", 1, datetime.now() - timedelta(hours=12), 1, 1))

        session.add(TaskExecutor(4, 2, 0))
        session.add(TaskExecutor(4, 3, 0))
        session.add(Task(2, "task2", "bla-bla", 2, datetime.now() - timedelta(hours=12), 1, None))
        await session.flush()

        await session.commit()

        if "postgresql" in get_settings().DB_URL:
            for table in ("rooms", "invitations", "orders", "tasks"):
                await session.execute(
                    text(
                        f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), ( SELECT MAX(id) FROM {table} ) + 1);"
                    )
                )
        await session.commit()

        yield

        await clear_db()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def clear_db_before_start():
    await clear_db()


"""
ERROR TESTS
"""


def test_register_exists():
    r = post("/bot/user/create", {"user_id": 1})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 101


def test_create_room_user_not_exist():
    r = post("/bot/room/create", {"user_id": 0, "room": {"name": "a"}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_invite_person_user_not_exist():
    r = post("/bot/invitation/create", {"user_id": 0, "addressee": {"alias": "me_not_exists"}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_accept_invitation_user_not_exist():
    r = post("/bot/invitation/accept", {"user_id": 0, "invitation": {"id": 1}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_create_order_user_not_exist():
    r = post("/bot/order/create", {"user_id": 0, "order": {"users": [1]}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_create_task_user_not_exist():
    r = post("/bot/task/create", {"user_id": 0, "task": {"name": "a", "start_date": 0, "period": 1, "order_id": 1}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_modify_task_user_not_exist():
    r = post(
        "/bot/task/modify", {"user_id": 0, "task": {"id": 1, "name": "a", "start_date": 0, "period": 1, "order_id": 1}}
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_remove_task_parameters_user_not_exist():
    r = post("/bot/task/remove_parameters", {"user_id": 0, "task": {"id": 1, "order_id": True}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_daily_info_user_not_exist():
    r = post("/bot/room/daily_info", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_incoming_invitations_user_not_exist():
    r = post("/bot/invitation/inbox", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_room_info_user_not_exist():
    r = post("/bot/room/info", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_leave_room_user_not_exist():
    r = post("/bot/room/leave", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_get_tasks_user_not_exist():
    r = post("/bot/task/list", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_get_task_info_user_not_exist():
    r = post("/bot/task/info", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_get_sent_invitations_user_not_exist():
    r = post("/bot/invitation/sent", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_delete_invitation_user_not_exist():
    r = post("/bot/invitation/delete", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_reject_invitation_user_not_exist():
    r = post("/bot/invitation/reject", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_get_order_info_user_not_exist():
    r = post("/bot/order/info", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_save_alias_user_not_exist():
    r = post("/bot/user/save_alias", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_save_fullname_user_not_exist():
    r = post("/bot/user/save_fullname", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_delete_task_user_not_exist():
    r = post("/bot/task/delete", {"user_id": 0, "task_id": 1})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_delete_order_user_not_exist():
    r = post("/bot/order/delete", {"user_id": 0, "order_id": 1})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_order_in_use_user_not_exist():
    r = post("/bot/order/is_in_use", {"user_id": 0, "order_id": 1})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


def test_list_of_orders_user_not_exist():
    r = post("/bot/room/list_of_orders", {"user_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 102


#############################


def test_create_room_user_has_room():
    r = post("/bot/room/create", {"user_id": 1, "room": {"name": "a"}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 106


# def test_invite_user_addressee_has_room():
#     r = post("/bot/invitation/create", {"user_id": 1, "addressee": {"id": 2}})
#     assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
#     assert r.json()["code"] == 106


def test_accept_invitation_user_has_room():
    r = post("/bot/invitation/accept", {"user_id": 4, "invitation": {"id": 2}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 106


def test_invite_user_user_has_no_room():
    r = post("/bot/invitation/create", {"user_id": 3, "addressee": {"alias": "no_room"}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_create_order_user_has_no_room():
    r = post("/bot/order/create", {"user_id": 3, "order": {"users": [1]}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_create_task_user_has_no_room():
    r = post("/bot/task/create", {"user_id": 3, "task": {"name": "a", "start_date": 0, "period": 1, "order_id": 1}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_modify_task_user_has_no_room():
    r = post(
        "/bot/task/modify", {"user_id": 3, "task": {"id": 1, "name": "a", "start_date": 0, "period": 1, "order_id": 1}}
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_remove_task_parameters_user_has_no_room():
    r = post("/bot/task/remove_parameters", {"user_id": 3, "task": {"id": 1, "order_id": True}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_daily_info_user_has_no_room():
    r = post("/bot/room/daily_info", {"user_id": 3})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_room_info_user_has_no_room():
    r = post("/bot/room/info", {"user_id": 3})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_leave_room_user_has_no_room():
    r = post("/bot/room/leave", {"user_id": 3})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_get_tasks_user_has_no_room():
    r = post("/bot/task/list", {"user_id": 3})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_get_task_info_user_has_no_room():
    r = post("/bot/task/info", {"user_id": 3})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_get_order_info_user_has_no_room():
    r = post("/bot/order/info", {"user_id": 3})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_delete_task_user_has_no_room():
    r = post("/bot/task/delete", {"user_id": 3, "task_id": 1})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_delete_order_user_has_no_room():
    r = post("/bot/order/delete", {"user_id": 3, "order_id": 1})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_order_in_use_user_has_no_room():
    r = post("/bot/order/is_in_use", {"user_id": 3, "order_id": 1})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


def test_list_of_orders_user_has_no_room():
    r = post("/bot/room/list_of_orders", {"user_id": 3})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 105


#########################


@pytest.mark.asyncio
async def test_invite_too_many():
    async with session_maker.get_session() as db:
        db.add(Room(1001, "1001"))
        await db.flush()
        db.add(User(1001, 1001))
        await db.flush()
        for i in range(get_settings().MAX_INVITATIONS):
            db.add(Invitation(id_=1001 + i, sender_id=1001, addressee_alias="durov", room_id=1001))
        await db.commit()
    r = post("/bot/invitation/create", {"user_id": 1001, "addressee": {"alias": "alias3"}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 109


@pytest.mark.asyncio
async def test_create_order_too_many():
    async with session_maker.get_session() as db:
        db.add(Room(1001, "1001"))
        await db.flush()
        db.add(User(1001, 1001))
        for i in range(get_settings().MAX_ORDERS):
            db.add(Order(id_=1001 + i, room_id=1001))
        await db.commit()
    r = post("/bot/order/create", {"user_id": 1001, "order": {"users": [1001]}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 113


@pytest.mark.asyncio
async def test_create_task_too_many():
    async with session_maker.get_session() as db:
        db.add(Room(1001, "1001"))
        await db.flush()
        db.add(User(1001, 1001))
        db.add(Order(1001, 1001))
        for i in range(get_settings().MAX_TASKS):
            db.add(Task(id_=1001 + i, name="1001", start_date=datetime.fromtimestamp(0), period=1, room_id=1001))
        await db.commit()
    r = post(
        "/bot/task/create",
        {"user_id": 1001, "task": {"name": "1001", "start_date": 0, "period": 1, "order_id": "1001"}},
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 114


def test_invite_already_sent():
    r = post("/bot/invitation/create", {"user_id": 1, "addressee": {"alias": "alias3"}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 110


def test_accept_invitation_not_exist():
    r = post("/bot/invitation/accept", {"user_id": 3, "invitation": {"id": 0}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 111


def test_delete_invitation_not_exist():
    r = post("/bot/invitation/delete", {"user_id": 3, "invitation": {"id": 0}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 111


def test_reject_invitation_not_exist():
    r = post("/bot/invitation/reject", {"user_id": 3, "invitation": {"id": 0}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 111


def test_accept_invitation_not_yours():
    r = post("/bot/invitation/accept", {"user_id": 5, "invitation": {"id": 1}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 112


def test_create_order_user_in_order_not_exist():
    r = post("/bot/order/create", {"user_id": 1, "order": {"users": [0]}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 116


def test_create_order_order_user_not_in_room():
    r = post("/bot/order/create", {"user_id": 1, "order": {"users": [3]}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 115


def test_create_task_order_not_exist():
    r = post("/bot/task/create", {"user_id": 1, "task": {"name": "one", "start_date": 0, "period": 1, "order_id": 0}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 107


def test_get_order_info_order_not_exist():
    r = post(
        "/bot/order/info",
        {"user_id": 1, "order": {"id": 0}},
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 107


def test_modify_task_task_not_exist():
    r = post(
        "/bot/task/modify",
        {"user_id": 1, "task": {"id": 0, "name": "one", "start_date": 0, "period": 1, "order_id": 1}},
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 108


def test_remove_task_parameters_task_not_exist():
    r = post(
        "/bot/task/remove_parameters",
        {"user_id": 1, "task": {"id": 0, "order_id": True}},
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 108


def test_get_task_info_task_not_exist():
    r = post(
        "/bot/task/info",
        {"user_id": 1, "task": {"id": 0}},
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 108


def test_modify_task_order_not_exist():
    r = post(
        "/bot/task/modify",
        {"user_id": 1, "task": {"id": 1, "name": "one", "start_date": 0, "period": 1, "order_id": 0}},
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 107


def test_modify_task_not_yours_task():
    r = post(
        "/bot/task/modify",
        {"user_id": 4, "task": {"id": 1, "name": "one", "start_date": 0, "period": 1, "order_id": 1}},
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 117


def test_modify_task_not_yours_order():
    r = post(
        "/bot/task/modify",
        {"user_id": 4, "task": {"id": 2, "name": "one", "start_date": 0, "period": 1, "order_id": 1}},
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 117


def test_remove_task_parameters_not_yours_task():
    r = post(
        "/bot/task/remove_parameters",
        {"user_id": 4, "task": {"id": 1, "order_id": True}},
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 117


def test_get_task_info_not_yours_task():
    r = post("/bot/task/info", {"user_id": 4, "task": {"id": 1}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 117


def test_get_order_info_not_yours_order():
    r = post("/bot/order/info", {"user_id": 4, "order": {"id": 1}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 117


def test_delete_invitation_not_yours_invitation():
    r = post("/bot/invitation/delete", {"user_id": 4, "invitation": {"id": 1}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 119


def test_reject_invitation_not_yours_invitation():
    r = post("/bot/invitation/reject", {"user_id": 2, "invitation": {"id": 1}})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 112


@pytest.mark.asyncio
async def test_accept_invitation_expired():
    async with session_maker.get_session() as db:
        db.add(
            Invitation(1001, 1, "lol", 1, datetime.now() - timedelta(days=get_settings().INVITATION_LIFESPAN_DAYS + 1))
        )
        await db.commit()
    r = post(
        "/bot/invitation/accept",
        {"user_id": 3, "invitation": {"id": 1001}},
    )
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 118


def test_delete_task_not_exist():
    r = post("/bot/task/delete", {"user_id": 1, "task_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 108


def test_delete_task_not_yours_task():
    r = post("/bot/task/delete", {"user_id": 1, "task_id": 2})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 117


def test_delete_order_not_exist():
    r = post("/bot/order/delete", {"user_id": 1, "order_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 107


def test_delete_order_not_yours_order():
    r = post("/bot/order/delete", {"user_id": 1, "order_id": 2})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 117


def test_order_in_use_not_exist():
    r = post("/bot/order/is_in_use", {"user_id": 1, "order_id": 0})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 107


def test_order_in_use_not_yours_order():
    r = post("/bot/order/is_in_use", {"user_id": 1, "order_id": 2})
    assert r.status_code == 400 and isinstance(r.json(), dict) and "code" in r.json()
    assert r.json()["code"] == 117


"""
SUCCESS TESTS
"""


def test_register():
    r = post("/bot/user/create", {"user_id": 1001})
    assert r.status_code == 200 and r.json() == 1001


@pytest.mark.asyncio
async def test_create_room():
    async with session_maker.get_session() as db:
        db.add(User(1001))
        await db.commit()
    r = post("/bot/room/create", {"user_id": 1001, "room": {"name": "1001"}})
    assert r.status_code == 200 and isinstance(r.json(), int)


@pytest.mark.asyncio
async def test_invite():
    async with session_maker.get_session() as db:
        db.add(Room(1001, "1001"))
        await db.flush()
        db.add(User(1001, 1001))
        await db.commit()
    r = post("/bot/invitation/create", {"user_id": 1001, "addressee": {"alias": "top_alias"}})
    assert r.status_code == 200 and isinstance(r.json(), int)


@pytest.mark.asyncio
async def test_accept_invitation():
    async with session_maker.get_session() as db:
        db.add(Room(1001, "1001"))
        await db.flush()
        db.add(User(1001, 1001))
        db.add(User(1002, alias="alias1002"))
        await db.flush()
        db.add(Invitation(1001, 1001, "alias1002", 1001))
        await db.commit()
    r = post("/bot/invitation/accept", {"user_id": 1002, "invitation": {"id": 1001}})
    assert r.status_code == 200 and r.json() == 1001


@pytest.mark.asyncio
async def test_create_order():
    async with session_maker.get_session() as db:
        db.add(Room(1001, "1001"))
        await db.flush()
        db.add_all([User(1001, 1001), User(1002, 1001)])
        await db.commit()
    r = post("/bot/order/create", {"user_id": 1001, "order": {"users": [1002, 1001]}})
    assert r.status_code == 200 and isinstance(r.json(), int)


@pytest.mark.asyncio
async def test_create_task():
    async with session_maker.get_session() as db:
        db.add(Room(1001, "1001"))
        await db.flush()
        db.add(User(1001, 1001))
        db.add(User(1002, 1001))
        await db.commit()
    order_id = post("/bot/order/create", {"user_id": 1001, "order": {"users": [1002, 1001]}}).json()
    r = post(
        "/bot/task/create",
        {
            "user_id": 1001,
            "task": {
                "name": "task1001",
                "description": "foo bar",
                "start_date": datetime.now().isoformat(),
                "period": 7,
                "order_id": order_id,
            },
        },
    )
    assert r.status_code == 200 and isinstance(r.json(), int)


@pytest.mark.asyncio
async def test_modify_task():
    async with session_maker.get_session() as db:
        db.add(Room(1001, "1001"))
        await db.flush()
        db.add(User(1001, 1001))
        await db.flush()
        db.add(Order(1001, 1001))
        db.add(TaskExecutor(1001, 1001, 1))
        db.add(Task(1001, "1001", "", 1001, datetime.now(), 1, 1001))
        await db.commit()

        r = post(
            "/bot/task/modify",
            {
                "user_id": 1001,
                "task": {
                    "id": 1001,
                    "name": "task1001",
                    "description": "foo bar",
                    "start_date": (start_date := datetime.now().isoformat()),
                    "period": 7,
                    "order_id": 1001,
                },
            },
        )
        assert r.status_code == 200 and r.json() is True

        task: Task = await db.get(Task, 1001)
        assert (
            task.name == "task1001"
            and task.description == "foo bar"
            and task.start_date == datetime.fromisoformat(start_date)
            and task.period == 7
            and task.order_id == 1001
        )


def setup_some_tasks():
    post("/bot/user/create", {"user_id": 1001})
    post("/bot/user/create", {"user_id": 1002})
    post("/bot/user/save_fullname", {"user_id": 1001, "fullname": "fullname1001"})
    post("/bot/user/save_alias", {"user_id": 1002, "alias": "alias1002"})
    post("/bot/room/create", {"user_id": 1001, "room": {"name": "1001"}})
    invitation = post("/bot/invitation/create", {"user_id": 1001, "addressee": {"alias": "alias1002"}}).json()
    post("/bot/invitation/accept", {"user_id": 1002, "invitation": {"id": invitation}})
    order_id = post("/bot/order/create", {"user_id": 1001, "order": {"users": [1001, 1002]}}).json()
    task1 = post(
        "/bot/task/create",
        {
            "user_id": 1001,
            "task": {
                "name": "task1001",
                "start_date": datetime.now().astimezone().isoformat(),
                "period": 1,
                "order_id": order_id,
            },
        },
    ).json()
    task2 = post(
        "/bot/task/create",
        {
            "user_id": 1001,
            "task": {
                "name": "task1002",
                "description": "description1002",
                "start_date": (datetime.now().astimezone() - timedelta(days=1)).isoformat(),
                "period": 1,
                "order_id": order_id,
            },
        },
    ).json()
    task_inactive_1 = post(
        "/bot/task/create",
        {
            "user_id": 1001,
            "task": {
                "name": "task1003",
                "start_date": (datetime.now().astimezone() + timedelta(days=1)).isoformat(),
                "period": 1,
                "order_id": order_id,
            },
        },
    ).json()
    task_inactive_2 = post(
        "/bot/task/create",
        {
            "user_id": 1001,
            "task": {
                "name": "task1004",
                "start_date": (datetime.now().astimezone() - timedelta(days=1)).isoformat(),
                "period": 1,
                "order_id": None,
            },
        },
    ).json()

    return task1, task2, task_inactive_1, task_inactive_2


@pytest.mark.asyncio
async def test_remove_task_parameters():
    t1, t2, _, _ = setup_some_tasks()
    r = post("/bot/task/remove_parameters", {"user_id": 1001, "task": {"id": t1, "order_id": True}})
    assert r.status_code == 200 and r.json() is True
    r = post("/bot/task/remove_parameters", {"user_id": 1001, "task": {"id": t2, "description": True}})
    assert r.status_code == 200 and r.json() is True
    async with session_maker.get_session() as db:
        assert (await db.get_one(Task, t1)).order_id is None and (await db.get_one(Task, t2)).description is None


def test_daily_info():
    task1, task2, task_inactive_1, task_inactive_2 = setup_some_tasks()
    r = post("/bot/room/daily_info", {"user_id": 1001})
    assert r.status_code == 200 and (
        len(tasks := r.json()["tasks"]) == 2
        and {"id": task1, "name": "task1001", "today_executor": {"id": 1001, "alias": None, "fullname": "fullname1001"}}
        in tasks
        and {"id": task2, "name": "task1002", "today_executor": {"id": 1002, "alias": "alias1002", "fullname": None}}
        in tasks
    )


def test_incoming_invitations():
    inv2 = post("/bot/invitation/create", {"user_id": 2, "addressee": {"alias": "alias3"}}).json()
    r = post("/bot/invitation/inbox", {"user_id": 3})
    assert r.status_code == 200 and (
        len(invites := r.json()["invitations"]) == 2
        and {"id": 1, "sender": {"id": 1, "alias": "alias1", "fullname": "name1"}, "room": 1, "room_name": "room1"}
        in invites
        and {"id": inv2, "sender": {"id": 2, "alias": None, "fullname": "full name2"}, "room": 1, "room_name": "room1"}
        in invites
    )

    r = post("/bot/invitation/inbox", {"user_id": 2})
    assert r.status_code == 200 and (len(r.json()["invitations"]) == 0)


def test_room_info():
    r = post("/bot/room/info", {"user_id": 1})
    assert r.status_code == 200 and (
        (info := r.json())["name"] == "room1"
        and info["id"] == 1
        and (
            len(users := list(info["users"])) == 2
            and {"id": 1, "fullname": "name1", "alias": "alias1"} in users
            and {"id": 2, "fullname": "full name2", "alias": None} in users
        )
    )


@pytest.mark.asyncio
async def test_leave_room():
    r = post("/bot/room/leave", {"user_id": 1})
    assert r.status_code == 200 and r.json() is True
    async with session_maker.get_session() as db:
        assert (await db.get(User, 1)).room_id is None and (
            await db.execute(select(exists(Room)).where(Room.id == 2))
        ).scalar()


@pytest.mark.asyncio
async def test_leave_room_delete_room():
    r = post("/bot/room/leave", {"user_id": 4})
    assert r.status_code == 200 and r.json() is True
    async with session_maker.get_session() as db:
        assert (await db.get(User, 4)).room_id is None and not (
            await db.execute(select(exists(Room)).where(Room.id == 2))
        ).scalar()


def test_get_task_list():
    task1, task2, task_inactive_1, task_inactive_2 = setup_some_tasks()
    r = post("/bot/task/list", {"user_id": 1001})
    assert r.status_code == 200 and (
        len(tasks := r.json()["tasks"]) == 4
        and {"id": task1, "name": "task1001", "inactive": False} in tasks
        and {"id": task2, "name": "task1002", "inactive": False} in tasks
        and {"id": task_inactive_1, "name": "task1003", "inactive": True} in tasks
        and {"id": task_inactive_2, "name": "task1004", "inactive": True} in tasks
    )


def test_get_task_info_active():
    r = post("/bot/task/info", {"user_id": 1, "task": {"id": 1}})
    assert r.status_code == 200
    t = TaskInfoResponse.model_validate(r.json())
    assert t == TaskInfoResponse(
        name="task1", description="bla-bla", start_date=t.start_date, period=1, order_id=1, inactive=False
    )


def test_get_task_info_inactive():
    r = post("/bot/task/info", {"user_id": 4, "task": {"id": 2}})
    assert r.status_code == 200
    t = TaskInfoResponse.model_validate(r.json())
    assert t == TaskInfoResponse(
        name="task2", description="bla-bla", start_date=t.start_date, period=1, order_id=None, inactive=True
    )


def test_get_sent_invitations():
    r = post("/bot/invitation/sent", {"user_id": 1})
    assert r.status_code == 200 and (
        len(invites := r.json()["invitations"]) == 2
        and {"id": 1, "addressee": "alias3", "room": 1, "room_name": "room1"} in invites
        and {"id": 2, "addressee": "alias4", "room": 2, "room_name": "room2"} in invites
    )


@pytest.mark.asyncio
async def test_delete_invitation():
    r = post("/bot/invitation/delete", {"user_id": 1, "invitation": {"id": 1}})
    assert r.status_code == 200 and r.json() is True
    async with session_maker.get_session() as db:
        assert await db.get(Invitation, 1) is None


@pytest.mark.asyncio
async def test_reject_invitation():
    r = post("/bot/invitation/reject", {"user_id": 3, "invitation": {"id": 1}})
    assert r.status_code == 200 and r.json() is True
    async with session_maker.get_session() as db:
        assert await db.get(Invitation, 1) is None


def test_get_order_info():
    r = post("/bot/order/info", {"user_id": 1, "order": {"id": 1}})
    assert r.status_code == 200 and r.json()["users"] == [
        {"id": 2, "alias": None, "fullname": "full name2"},
        {"id": 1, "alias": "alias1", "fullname": "name1"},
    ]


@pytest.mark.asyncio
async def test_save_alias():
    r1 = post("/bot/user/save_alias", {"user_id": 1, "alias": None})
    r2 = post("/bot/user/save_alias", {"user_id": 2, "alias": "alias2"})
    assert 200 == r1.status_code == r2.status_code and r1.json() and r2.json()
    async with session_maker.get_session() as db:
        assert (await db.get(User, 1)).alias is None
        assert (await db.get(User, 2)).alias == "alias2"


@pytest.mark.asyncio
async def test_save_fullname():
    r = post("/bot/user/save_fullname", {"user_id": 1, "fullname": "fullname1"})
    assert r.status_code == 200 and r.json()
    async with session_maker.get_session() as db:
        assert (await db.get(User, 1)).fullname == "fullname1"


@pytest.mark.asyncio
async def test_delete_task():
    r = post("/bot/task/delete", {"user_id": 1, "task_id": 1})
    assert r.status_code == 200 and r.json()
    async with session_maker.get_session() as db:
        assert (await db.get(Task, 1)) is None


@pytest.mark.asyncio
async def test_delete_order():
    r = post("/bot/order/delete", {"user_id": 1, "order_id": 1})
    assert r.status_code == 200 and r.json()
    async with session_maker.get_session() as db:
        assert (await db.get(Order, 1)) is None
        assert (await db.get(TaskExecutor, (2, 1, 0))) is None
        assert (await db.get(TaskExecutor, (1, 1, 1))) is None


def test_order_in_use():
    r = post("/bot/order/is_in_use", {"user_id": 1, "order_id": 1})
    assert r.status_code == 200 and r.json()
    r = post("/bot/order/is_in_use", {"user_id": 4, "order_id": 2})
    assert r.status_code == 200 and not r.json()


def test_list_of_orders():
    r = post("/bot/room/list_of_orders", {"user_id": 1})
    assert (
        r.status_code == 200
        and r.json()["orders"] == {"1": [2, 1]}
        and (
            len(users := r.json()["users"]) == 2
            and {"id": 1, "alias": "alias1", "fullname": "name1"} in users
            and {"id": 2, "alias": None, "fullname": "full name2"} in users
        )
    )

    r = post("/bot/room/list_of_orders", {"user_id": 4})
    assert (
        r.status_code == 200
        and r.json()["orders"] == {"2": [4], "3": [4]}
        and (len(users := r.json()["users"]) == 1 and users[0] == {"id": 4, "alias": None, "fullname": None})
    )
