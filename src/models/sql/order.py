import typing

from sqlalchemy.orm import Mapped, relationship

from src.models.sql import Base
from src.models.sql.mixins import IdMixin

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.task import Task
    from src.models.sql.executor import Executor


class Order(Base, IdMixin):
    __tablename__ = "orders"

    users: Mapped[list["User"]] = relationship(back_populates="orders", secondary="executors", viewonly=True)
    executors: Mapped[list["Executor"]] = relationship(back_populates="order")
    tasks: Mapped[list["Task"]] = relationship(back_populates="order")
