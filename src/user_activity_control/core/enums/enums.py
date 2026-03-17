from enum import Enum


class ProjectFoldersEnum(str, Enum):
    APP_DATA = "app_data"
    CONFIG = "config"
    EXAMPLES = "examples"
    STRINGS = "strings"
    USERS_CONFIG = "users_config"


class ExamplesFilesEnum(str, Enum):
    TEMPLATES = "templates_example.yaml"
    ALARM = "alarm_example.yaml"
    STAND_DOWN = "stand_down_example.yaml"
    COMMAND = "command_example.yaml"


class StringsFilesEnum(str, Enum):
    TEMPLATES = "templates.yaml"
    ALARM = "alarm.yaml"
    STAND_DOWN = "stand_down.yaml"
    COMMAND = "command.yaml"


class UsersConfigFilesEnum(str, Enum):
    CATEGORIES = "categories.yaml"
    USERS = "users.yaml"
