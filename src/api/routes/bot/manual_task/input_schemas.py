from pydantic import BaseModel, Field


class CreateManualTaskBody(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field("", max_length=1000)
    order_id: int | None = None


class ModifyManualTaskBody(BaseModel):
    id: int
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=3000)
    order_id: int | None = None


class RemoveManualTaskParametersBody(BaseModel):
    id: int
    description: bool | None = False
    order_id: bool | None = False
