from enum import Enum


class CommonCommandEnum(str, Enum):
    ABOUT = "about"


class AdminCommandEnum(str, Enum):
    START = "start"
