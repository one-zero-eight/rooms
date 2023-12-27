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
    description: Mapped[Optional[str]]
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="CASCADE"))
    start_date: Mapped[datetime]
    period: Mapped[int]  # in days
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id", onupdate="CASCADE", ondelete="SET NULL"))

    order: Mapped[Optional["Order"]] = relationship(back_populates="tasks", lazy="joined")

    def __init__(
        self,
        id_: int = None,
        name: str = None,
        description: str = None,
        room_id: int = None,
        start_date: datetime = None,
        period: int = None,
        order_id: int = None,
    ):
        super().__init__(
            id=id_,
            name=name,
            description=description,
            room_id=room_id,
            start_date=start_date,
            period=period,
            order_id=order_id,
        )

    def __repr__(self):
        return (
            f"Task(id={self.id}, name={repr(self.name)}, description={repr(self.description)}, room_id={self.room_id}, "
            f"start_date={repr(self.start_date)}, period={self.period}, order_id={self.order_id})"
        )
