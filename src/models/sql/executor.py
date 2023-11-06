import typing

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.sql.base import Base

if typing.TYPE_CHECKING:
    from src.models.sql.user import User
    from src.models.sql.order import Order


class Executor(Base):
    __tablename__ = "executors"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.telegram_id", onupdate="cascade", ondelete="cascade"), primary_key=True, autoincrement=False
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", onupdate="cascade", ondelete="cascade"), primary_key=True, autoincrement=False
    )
    # autoincrement doesn't work with PostgreSQL for some reason
    order_number: Mapped[int] = mapped_column(Identity(start=1, increment=1), autoincrement=True)

    user: Mapped["User"] = relationship(back_populates="executors")
    order: Mapped["Order"] = relationship(back_populates="executors")
