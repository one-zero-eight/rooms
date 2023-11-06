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
