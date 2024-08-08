from sqlalchemy import ForeignKey, Column, BigInteger
from sqlmodel import SQLModel, Field

# if typing.TYPE_CHECKING:
#     from src.models.sql.user import User
#     from src.models.sql.order import Order


class TaskExecutor(SQLModel, table=True):
    __tablename__ = "executors"
    # __table_args__ = (UniqueConstraint("order_id", "order_number"),)

    user_id: int = Field(
        sa_column=Column(
            BigInteger(),
            ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )
    )
    order_id: int = Field(
        sa_column_args=(ForeignKey("orders.id", onupdate="CASCADE", ondelete="CASCADE"),),
        primary_key=True,
        sa_column_kwargs={"autoincrement": False},
    )
    order_number: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": False})

    # user: "User" = Relationship(back_populates="executors", sa_relationship_kwargs={"lazy": "joined"})
    # order: "Order" = Relationship(back_populates="executors", sa_relationship_kwargs={"lazy": "joined"})

    def __init__(
        self,
        user_id: int = None,
        order_id: int = None,
        order_number: int = None,
    ):
        super().__init__(user_id=user_id, order_id=order_id, order_number=order_number)

    def __repr__(self):
        return f"TaskExecutor(user_id={self.user_id}, order_id={self.order_id}, order_number={self.order_number})"
