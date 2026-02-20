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
    INACTIVITY_ALERT_DELAY = "inactivity_alert_delay"
    STAND_DOWN_DELAY = "stand_down_delay"
    UNIQUE_COMMAND_REACTION = "unique_command_reactions"


class UserUniqueCommandReactionsEnum(Enum):
    ON = True
    OFF = False
