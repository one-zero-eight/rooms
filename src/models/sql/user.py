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
    from src.models.sql.executor import Executor


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    room_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="SET NULL"))
    register_datetime: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())

    room: Mapped["Room"] = relationship(back_populates="users")
    # invitations: Mapped[list["Invitation"]] = relationship()
    orders: Mapped[list["Order"]] = relationship(back_populates="users", secondary="executors", viewonly=True)
    executors: Mapped[list["Executor"]] = relationship(back_populates="user")
