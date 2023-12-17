from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.config import get_settings


class SqlAlchemySessionMaker:
    _engine: AsyncEngine
    _session_maker: async_sessionmaker

    def __init__(self, e: AsyncEngine):
        self._engine = e
        self._session_maker = async_sessionmaker(e, expire_on_commit=False)

    def get_session(self) -> AsyncSession:
        return self._session_maker()


engine = create_async_engine(get_settings().DB_URL)
sessionmaker = SqlAlchemySessionMaker(engine)


async def get_session():
    async with sessionmaker.get_session() as session:
        yield session


DB_SESSION_DEPENDENCY = Annotated[AsyncSession, Depends(get_session)]
