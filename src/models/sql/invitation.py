import typing

from sqlalchemy import ForeignKey
from sqlmodel import SQLModel, Field, Relationship

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.room import Room


class Invitation(SQLModel, table=True):
    __tablename__ = "invitations"

    id: int = Field(primary_key=True)
    sender_id: int = Field(sa_column_args=(ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),))
    addressee_alias: str = Field(max_length=64)
    room_id: int = Field(sa_column_args=(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="CASCADE"),))

    sender: "User" = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    room: "Room" = Relationship(back_populates="invitations", sa_relationship_kwargs={"lazy": "joined"})

    def __init__(
        self,
        id_: int = None,
        sender_id: int = None,
        addressee_alias: str = None,
        room_id: int = None,
    ):
        super().__init__(id=id_, sender_id=sender_id, addressee_alias=addressee_alias, room_id=room_id)

    def __repr__(self):
        return (
            f"Invitation(id={self.id}, sender_id={self.sender_id}, addressee_alias={self.addressee_alias}, "
            f"room_id={self.room_id})"
        )
