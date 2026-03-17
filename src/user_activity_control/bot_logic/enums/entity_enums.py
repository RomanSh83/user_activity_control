from enum import Enum


class EntityEnum(str, Enum):
    CATEGORY = "category"
    USER = "user"


class CategoryEnum(str, Enum):
    CATEGORY_ID = "category_id"
    NAME = "name"


class UsersEnum(str, Enum):
    USER_ID = "user_id"
    CATEGORY = "category"
    CHAT_IDS = "chat_ids"
    ALERT_REACTIONS = "alert_reactions"
    INACTIVITY_ALERT_DELAY = "inactivity_alert_delay"
    STAND_DOWN_REACTIONS = "stand_down_reactions"
    UNIQUE_COMMAND_REACTION = "unique_command_reactions"


class UserUniqueCommandReactionsEnum(Enum):
    ON = True
    OFF = False
