import typing

from sqlmodel import SQLModel, Relationship, Field

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.invitation import Invitation
    from src.models.sql.task import Task
    from src.models.sql.order import Order


class Room(SQLModel, table=True):
    __tablename__ = "rooms"

    id: int = Field(primary_key=True)
    name: str

    users: list["User"] = Relationship(back_populates="room", sa_relationship_kwargs={"lazy": "joined"})
    invitations: list["Invitation"] = Relationship(back_populates="room", sa_relationship_kwargs={"lazy": "joined"})
    tasks: list["Task"] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    orders: list["Order"] = Relationship(back_populates="room", sa_relationship_kwargs={"lazy": "joined"})

    def __init__(self, id_: int = None, name: str = None):
        super().__init__(id=id_, name=name)

    def __repr__(self):
        return f"Room(id={self.id}, name={repr(self.name)})"
