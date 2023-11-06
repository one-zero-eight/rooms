import typing

from sqlalchemy.orm import Mapped, relationship

from src.models.sql.base import Base
from src.models.sql.mixins import IdMixin

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.invitation import Invitation
    from src.models.sql.task import Task


class Room(Base, IdMixin):
    __tablename__ = "rooms"

    name: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="room")
    invitations: Mapped[list["Invitation"]] = relationship(back_populates="room")
    tasks: Mapped[list["Task"]] = relationship()
