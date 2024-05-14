import typing
from datetime import datetime, timedelta

from sqlalchemy import ForeignKey
from sqlmodel import SQLModel, Field, Relationship

from src.config import get_settings

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.room import Room


class Invitation(SQLModel, table=True):
    __tablename__ = "invitations"

    id: int = Field(primary_key=True)
    sender_id: int = Field(sa_column_args=(ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),))
    addressee_alias: str = Field(max_length=64, index=True)
    room_id: int = Field(sa_column_args=(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="CASCADE"),))
    expiration_date: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(days=get_settings().INVITATION_LIFESPAN_DAYS)
    )

    sender: "User" = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    room: "Room" = Relationship(back_populates="invitations", sa_relationship_kwargs={"lazy": "joined"})

    def __init__(
        self,
        id_: int = None,
        sender_id: int = None,
        addressee_alias: str = None,
        room_id: int = None,
        expiration_date: datetime = None,
    ):
        super().__init__(
            id=id_,
            sender_id=sender_id,
            addressee_alias=addressee_alias,
            room_id=room_id,
            expiration_date=expiration_date,
        )

    def __repr__(self):
        return (
            f"Invitation(id={self.id}, sender_id={self.sender_id}, addressee_alias={self.addressee_alias}, "
            f"room_id={self.room_id}, expiration_date={self.expiration_date})"
        )
