import typing

from sqlalchemy import ForeignKey
from sqlmodel import SQLModel, Field, Relationship

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.task import Task
    from src.models.sql.task_executor import TaskExecutor
    from src.models.sql.room import Room


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: int = Field(primary_key=True)
    room_id: int = Field(sa_column_args=(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="CASCADE"),))

    room: "Room" = Relationship(back_populates="orders", sa_relationship_kwargs={"lazy": "joined"})
    users: list["User"] = Relationship(
        back_populates="orders", sa_relationship_kwargs={"lazy": "joined", "secondary": "executors", "viewonly": True}
    )
    executors: list["TaskExecutor"] = Relationship(back_populates="order", sa_relationship_kwargs={"lazy": "joined"})
    tasks: list["Task"] = Relationship(back_populates="order", sa_relationship_kwargs={"lazy": "joined"})

    def __init__(self, id_: int = None, room_id: int = None):
        super().__init__(id=id_, room_id=room_id)

    def __repr__(self):
        return f"Order(id={self.id})"
