from datetime import timedelta, datetime
from typing import Annotated

from fastapi import Header, Depends

# noinspection PyPackageRequirements
from jose import jwt, ExpiredSignatureError, JWTError

from src.api.exceptions import (
    NoTokenException,
    TelegramBotAccessException,
    TokenExpiredException,
    InvalidTokenException,
)
from src.config import get_settings

settings = get_settings()


def create_jwt(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta is not None:
        expire = (datetime.utcnow() + expires_delta).timestamp()
    else:
        expire = -1
    to_encode.update({"expire": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM)
    return encoded_jwt


def decode_jwt(token: str):
    payload = jwt.decode(token, settings.SECRET_KEY, settings.TOKEN_ALGORITHM)
    if "expire" not in payload or payload["expire"] < datetime.utcnow().timestamp() and payload["expire"] != -1:
        raise ExpiredSignatureError()
    return payload


def verify_bot_access(x_token: Annotated[str | None, Header()] = None):
    if x_token is None:
        raise NoTokenException()
    try:
        data = decode_jwt(x_token)
        if not data["sub"] == "tgbot":
            raise TelegramBotAccessException()
        return True
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise InvalidTokenException()


BOT_ACCESS_DEPENDENCY = Depends(verify_bot_access)
