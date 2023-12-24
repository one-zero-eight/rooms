import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.sql.base import Base

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.order import Order


class TaskExecutor(Base):
    __tablename__ = "executors"
    __table_args__ = (UniqueConstraint("order_id", "order_number"),)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", onupdate="cascade", ondelete="cascade"), primary_key=True, autoincrement=False
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", onupdate="cascade", ondelete="cascade"), primary_key=True, autoincrement=False
    )
    order_number: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)

    user: Mapped["User"] = relationship(back_populates="executors", lazy="joined")
    order: Mapped["Order"] = relationship(back_populates="executors", lazy="joined")

    def __init__(
        self,
        user_id: int = None,
        order_id: int = None,
        order_number: int = None,
    ):
        super().__init__(user_id=user_id, order_id=order_id, order_number=order_number)

    def __repr__(self):
        return f"TaskExecutor(user_id={self.user_id}, order_id={self.order_id}, order_number={self.order_number})"
