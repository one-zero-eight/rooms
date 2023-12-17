from src.schemas.utils import MyBaseModel


class BaseRoom(MyBaseModel):
    name: str


class CreateRoom(BaseRoom):
    pass


class Room(BaseRoom):
    id: int
