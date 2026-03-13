from pydantic import BaseModel, RootModel


class StringsItemSchema(BaseModel):
    alarm: list[str] = []
    command: list[str] = []
    templates: dict[str, str] = {}
    stand_down: list[str] = []


class StringsCollectionSchema(RootModel):
    root: dict[str, StringsItemSchema]
