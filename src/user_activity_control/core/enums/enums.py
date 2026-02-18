from enum import Enum


class ProjectFoldersEnum(str, Enum):
    APP_DATA = "app_data"
    CONFIG = "config"
    EXAMPLES = "examples"
    STRINGS = "strings"
    USERS_CONFIG = "users_config"


class AppDataFilesEnum(str, Enum):
    CATEGORIES = "categories.yaml"
    USERS = "users.yaml"
