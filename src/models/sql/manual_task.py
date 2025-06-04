from typing import Optional

from sqlalchemy import ForeignKey
from sqlmodel import SQLModel, Field


# if typing.TYPE_CHECKING:
#     from src.models.sql.order import Order


class ManualTask(SQLModel, table=True):
    __tablename__ = "manual_tasks"

    id: int = Field(primary_key=True)
    room_id: int = Field(sa_column_args=(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="CASCADE"),))
    name: str
    description: Optional[str]
    counter: int = Field(sa_column_kwargs={"server_default": "0"})
    order_id: Optional[int] = Field(sa_column_args=(ForeignKey("orders.id", onupdate="CASCADE", ondelete="SET NULL"),))

    # order: Optional["Order"] = Relationship(back_populates="tasks", sa_relationship_kwargs={"lazy": "joined"})

    def __init__(
        self,
        id_: int = None,
        room_id: int = None,
        name: str = None,
        description: str = None,
        counter: int = 0,
        order_id: int = None,
    ):
        super().__init__(
            id=id_,
            name=name,
            description=description,
            room_id=room_id,
            counter=counter,
            order_id=order_id,
        )

    def is_inactive(self) -> bool:
        return self.order_id is None
