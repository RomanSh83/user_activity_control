from pydantic import BaseModel


class ControlUserSchema(BaseModel):
    id: int
    type: str
    chat_ids: set[int]
    inactivity_alert_delay: int
    stand_down_delay: int
    unique_command_reactions: bool
