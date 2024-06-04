from functools import lru_cache, cached_property
from typing import Annotated

import dotenv
from fastapi import Depends
from pydantic_settings import BaseSettings


class _DockerSecrets(BaseSettings):
    DB_PASSWORD_FILE: str | None = None

    @cached_property
    def db_password(self) -> str | None:
        if self.DB_PASSWORD_FILE:
            with open(self.DB_PASSWORD_FILE) as f:
                return f.read().strip()
        return None


# noinspection PyPep8Naming
class Settings(BaseSettings):
    DB_DRIVER: str
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str | None = None
    DB_NAME: str
    SECRET_KEY: str
    TOKEN_ALGORITHM: str
    MAX_INVITATIONS: int
    MAX_ORDERS: int
    MAX_TASKS: int
    INVITATION_LIFESPAN_DAYS: int

    _docker_secrets: _DockerSecrets

    @cached_property
    def DB_URL(self) -> str:
        password = self._docker_secrets.db_password or self.DB_PASSWORD
        if not password:
            raise RuntimeError("A DB password is not specified!")
        return "{driver}://{user}:{password}@{host}/{name}".format(
            driver=self.DB_DRIVER,
            user=self.DB_USER,
            password=password,
            host=self.DB_HOST,
            name=self.DB_NAME,
        )

    def __init__(self):
        super().__init__(_env_file=None)
        self._docker_secrets = _DockerSecrets()


@lru_cache
def get_settings():
    if dotenv.find_dotenv():
        dotenv.load_dotenv()
    return Settings()


SETTINGS_DEPENDENCY = Annotated[Settings, Depends(get_settings)]
