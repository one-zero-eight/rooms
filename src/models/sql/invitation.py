import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.sql.mixins import IdMixin
from src.models.sql.base import Base

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.room import Room


class Invitation(Base, IdMixin):
    __tablename__ = "invitations"

    sender_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id", onupdate="CASCADE", ondelete="CASCADE"))
    adressee_id: Mapped[int]
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="CASCADE"))

    sender: Mapped["User"] = relationship()
    room: Mapped["Room"] = relationship(back_populates="invitations")

    def __init__(
        self,
        id_: int = None,
        sender_id: int = None,
        adressee_id: int = None,
        room_id: int = None,
        sender: "User" = None,
        room: "Room" = None,
    ):
        super().__init__(
            id=id_, sender_id=sender_id, adressee_id=adressee_id, room_id=room_id, sender=sender, room=room
        )

    def __repr__(self):
        return (
            f"Invitation(id={self.id}, sender_id={self.sender_id}, adressee_id={self.adressee_id}, "
            f"room_id={self.room_id})"
        )
