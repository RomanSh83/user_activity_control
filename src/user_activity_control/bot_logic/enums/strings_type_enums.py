from enum import Enum


class StringsTypesEnum(str, Enum):
    ALARM = "alarm"
    COMMAND = "command"
    STAND_DOWN = "stand_down"
    TEMPLATES = "templates"
