import typing
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, func, BigInteger, Column
from sqlmodel import SQLModel, Field, Relationship

if typing.TYPE_CHECKING:
    from src.models.sql.room import Room

    # from src.models.sql.invitation import Invitation
    from src.models.sql.order import Order
    from src.models.sql.task_executor import TaskExecutor


class User(SQLModel, table=True):
    __tablename__ = "users"

    # User's telegram id
    id: int = Field(sa_column=Column(BigInteger(), primary_key=True, autoincrement=False))
    alias: str | None = Field(max_length=255, nullable=True, default=None, index=True)
    fullname: str | None = Field(max_length=255, nullable=True, default=None)
    room_id: int | None = Field(sa_column_args=(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="SET NULL"),))
    register_datetime: datetime | None = Field(sa_column_kwargs={"server_default": func.now()})

    room: Optional["Room"] = Relationship(back_populates="users", sa_relationship_kwargs={"lazy": "joined"})
    # invitations: list["Invitation"] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    orders: list["Order"] = Relationship(
        back_populates="users", sa_relationship_kwargs={"lazy": "joined", "secondary": "executors", "viewonly": True}
    )
    executors: list["TaskExecutor"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "joined"})

    def __init__(
        self,
        id_: int = None,
        room_id: int = None,
        alias: str | None = None,
        fullname: str | None = None,
        register_datetime: datetime = None,
    ):
        super().__init__(id=id_, room_id=room_id, alias=alias, fullname=fullname, register_datetime=register_datetime)

    def __repr__(self):
        return (
            f'User(id={self.id}, alias="{self.alias}", fullname="{self.fullname}", '
            f"room_id={self.room_id}, register_datetime={repr(self.register_datetime)})"
        )
