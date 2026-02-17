from pydantic import BaseModel


class UserSchema(BaseModel):
    user_id: str
    category: str
    chat_ids: list[str]
    inactivity_alert_delay: int
    stand_down_delay: int
    unique_command_reactions: bool


class UserUpdateSchema(BaseModel):
    category: str | None = None
    chat_ids: list[str] | None = None
    inactivity_alert_delay: int | None = None
    stand_down_delay: int | None = None
    unique_command_reactions: bool | None = None
