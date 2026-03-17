from pydantic import BaseModel, RootModel


class UserParamsSchema(BaseModel):
    category: str
    chat_ids: list[str]
    alert_reactions: bool
    inactivity_alert_delay: int
    stand_down_reactions: bool
    unique_command_reactions: bool


class UserSchema(UserParamsSchema):
    user_id: str


class UserParamsUpdateSchema(BaseModel):
    category: str | None = None
    chat_ids: list[str] | None = None
    alert_reactions: bool | None = None
    inactivity_alert_delay: int | None = None
    stand_down_reactions: bool | None = None
    unique_command_reactions: bool | None = None


class UsersSchema(RootModel):
    root: dict[str, UserParamsSchema]
