from src.schemas.utils import MyBaseModel


class BaseRoomSchema(MyBaseModel):
    name: str


class CreateRoomSchema(BaseRoomSchema):
    pass


class RoomSchema(BaseRoomSchema):
    id: int
