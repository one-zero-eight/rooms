from sqlalchemy import ForeignKey
from sqlmodel import SQLModel, Field


class Rule(SQLModel, table=True):
    __tablename__ = "rules"

    id: int = Field(primary_key=True)
    name: str
    text: str
    room_id: int = Field(sa_column_args=(ForeignKey("rooms.id", onupdate="CASCADE", ondelete="CASCADE"),))

    def __init__(self, id_: int = None, name: str = None, text: str = None, room_id: int = None):
        super().__init__(
            id=id_,
            name=name,
            text=text,
            room_id=room_id,
        )

    def __repr__(self):
        return f"Rule(id={self.id}, name={repr(self.name)}, text={repr(self.text)}, room_id={self.room_id})"
