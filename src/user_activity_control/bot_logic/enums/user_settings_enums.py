from enum import Enum


class UserSettingsEnum(str, Enum):
    TYPE = "type"
    CHAT_IDS = "chat_ids"
    INACTIVITY_ALERT_DELAY = "inactivity_alert_delay"
    STAND_DOWN_DELAY = "stand_down_delay"
    UNIQUE_COMMAND_REACTION = "unique_command_reactions"
