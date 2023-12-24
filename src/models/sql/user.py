import typing
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.sql.base import Base

if typing.TYPE_CHECKING:
    from src.models.sql.room import Room

    # from src.models.sql.invitation import Invitation
    from src.models.sql.order import Order
    from src.models.sql.task_executor import TaskExecutor


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="SET NULL"))
    register_datetime: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())

    room: Mapped["Room"] = relationship(back_populates="users", lazy="joined")
    # invitations: Mapped[list["Invitation"]] = relationship(lazy="joined")
    orders: Mapped[list["Order"]] = relationship(
        back_populates="users", secondary="executors", viewonly=True, lazy="joined"
    )
    executors: Mapped[list["TaskExecutor"]] = relationship(back_populates="user", lazy="joined")

    def __init__(
        self,
        id_: int = None,
        room_id: int = None,
        register_datetime: datetime = None,
    ):
        super().__init__(id=id_, room_id=room_id, register_datetime=register_datetime)

    def __repr__(self):
        return f"User(id={self.id}, room_id={self.room_id}, " f"register_datetime={repr(self.register_datetime)})"
