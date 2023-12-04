import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY: str
    TOKEN_ALGORITHM: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings(_env_file=os.getenv("DOTENV_PATH", ".env"))


SETTINGS_DEPENDENCY = Annotated[Settings, Depends(get_settings)]
