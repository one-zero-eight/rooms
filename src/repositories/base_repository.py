from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


class BaseSqlAlchemyRepository:
    _engine: AsyncEngine
    _session_maker: async_sessionmaker

    def __init__(self, engine: AsyncEngine):
        self._engine = engine
        self._session_maker = async_sessionmaker(engine)

    def _get_session(self) -> AsyncSession:
        return self._session_maker()
