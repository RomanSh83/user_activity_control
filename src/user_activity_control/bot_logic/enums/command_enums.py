from enum import Enum


class ChatCommandEnum(str, Enum):
    ABOUT = "about"


class PrivateCommandEnum(str, Enum):
    START = "start"
