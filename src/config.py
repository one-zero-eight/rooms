import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY: str
    TOKEN_ALGORITHM: str
    MAX_INVITATIONS: int
    MAX_ORDERS: int
    MAX_TASKS: int
    INVITATION_LIFESPAN_DAYS: int

    model_config = SettingsConfigDict(env_file=".env")

    def __init__(self):
        super().__init__(_env_file=os.getenv("DOTENV_PATH", ".env"))


@lru_cache
def get_settings():
    return Settings()


SETTINGS_DEPENDENCY = Annotated[Settings, Depends(get_settings)]
