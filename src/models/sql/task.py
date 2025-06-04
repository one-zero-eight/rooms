from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlmodel import SQLModel, Field

# if typing.TYPE_CHECKING:
#     from src.models.sql.order import Order


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int = Field(primary_key=True)
    name: str
    description: Optional[str]
    room_id: int = Field(sa_column_args=(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="CASCADE"),))
    start_date: datetime
    period: int  # in days
    order_id: Optional[int] = Field(sa_column_args=(ForeignKey("orders.id", onupdate="CASCADE", ondelete="SET NULL"),))

    # order: Optional["Order"] = Relationship(back_populates="tasks", sa_relationship_kwargs={"lazy": "joined"})

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

    def is_inactive(self) -> bool:
        return self.order_id is None or self.start_date > datetime.now()

    def is_today_duty(self, now: datetime) -> bool:
        return (now - self.start_date).days % self.period == 0

    def get_today_executor_index(self, now: datetime, executors_count: int) -> int:
        return (now - self.start_date).days // self.period % executors_count
