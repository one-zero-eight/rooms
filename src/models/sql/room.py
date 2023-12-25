import typing

from sqlalchemy.orm import Mapped, relationship

from src.models.sql.base import Base
from src.models.sql.mixins import IdMixin

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.invitation import Invitation
    from src.models.sql.task import Task
    from src.models.sql.order import Order


class Room(Base, IdMixin):
    __tablename__ = "rooms"

    name: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="room", lazy="joined")
    invitations: Mapped[list["Invitation"]] = relationship(back_populates="room", lazy="joined")
    tasks: Mapped[list["Task"]] = relationship(lazy="joined")
    orders: Mapped[list["Order"]] = relationship(back_populates="room", lazy="joined")

    def __init__(self, id_: int = None, name: str = None):
        super().__init__(id=id_, name=name)

    def __repr__(self):
        return f"Room(id={self.id}, name={repr(self.name)})"
