import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.models.sql import Base
from src.models.sql.mixins import IdMixin

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.task import Task
    from src.models.sql.task_executor import TaskExecutor
    from src.models.sql.room import Room


class Order(Base, IdMixin):
    __tablename__ = "orders"

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="CASCADE"))

    room: Mapped["Room"] = relationship(back_populates="orders", lazy="joined")
    users: Mapped[list["User"]] = relationship(
        back_populates="orders", secondary="executors", viewonly=True, lazy="joined"
    )
    executors: Mapped[list["TaskExecutor"]] = relationship(back_populates="order", lazy="joined")
    tasks: Mapped[set["Task"]] = relationship(back_populates="order", lazy="joined")

    def __init__(self, id_: int = None, room_id: int = None):
        super().__init__(id=id_, room_id=room_id)

    def __repr__(self):
        return f"Order(id={self.id})"
