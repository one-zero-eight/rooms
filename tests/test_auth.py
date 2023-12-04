from datetime import timedelta, datetime

import pytest
from fastapi.testclient import TestClient

from src.api.auth.utils import create_jwt, decode_jwt
from src.config import get_settings
from src.main import app as main_app
from src.api.auth.utils import BOT_ACCESS_DEPENDENCY


@main_app.get("/test_bot_access", dependencies=[BOT_ACCESS_DEPENDENCY])
def bot_access():
    return "ok"


client = TestClient(main_app)


@pytest.fixture()
def replace_secret():
    settings = get_settings()
    key = settings.SECRET_KEY
    settings.SECRET_KEY = "12345"
    yield
    settings.SECRET_KEY = key


@pytest.mark.usefixtures("replace_secret")
def test_jwt_generation():
    token = create_jwt({"sub": "tgbot"}, expires_delta=timedelta(minutes=20))
    decoded = decode_jwt(token)
    assert "sub" in decoded
    assert decoded["sub"] == "tgbot"
    assert "expire" in decoded
    assert abs(decoded["expire"] - (datetime.utcnow() + timedelta(minutes=20)).timestamp()) <= 5


def test_bot_access_granted():
    token = create_jwt({"sub": "tgbot"}, expires_delta=timedelta(seconds=30))
    response = client.get("/test_bot_access", headers={"X-Token": token})
    assert response.status_code == 200
    assert response.json() == "ok"


def test_bot_access_denied():
    response = client.get("/test_bot_access")
    assert response.status_code == 401

    token = create_jwt({"sub": "me"}, expires_delta=timedelta(seconds=30))
    response = client.get("/test_bot_access", headers={"X-Token": token})
    assert response.status_code == 401
