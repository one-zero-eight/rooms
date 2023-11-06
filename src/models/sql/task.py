import typing
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.sql.base import Base
from src.models.sql.mixins import IdMixin

if typing.TYPE_CHECKING:
    from src.models.sql.order import Order


class Task(Base, IdMixin):
    __tablename__ = "tasks"

    name: Mapped[str]
    descriprion: Mapped[Optional[str]]
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="CASCADE"))
    start_date: Mapped[datetime]
    period: Mapped[int]  # in days
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id", onupdate="CASCADE", ondelete="SET NULL"))

    order: Mapped["Order"] = relationship(back_populates="tasks")
