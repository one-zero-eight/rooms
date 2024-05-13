from functools import lru_cache
from typing import Annotated

import dotenv
from fastapi import Depends
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY: str
    TOKEN_ALGORITHM: str
    MAX_INVITATIONS: int
    MAX_ORDERS: int
    MAX_TASKS: int
    INVITATION_LIFESPAN_DAYS: int

    def __init__(self):
        super().__init__(_env_file=None)


@lru_cache
def get_settings():
    if dotenv.find_dotenv():
        dotenv.load_dotenv()
    return Settings()


SETTINGS_DEPENDENCY = Annotated[Settings, Depends(get_settings)]
