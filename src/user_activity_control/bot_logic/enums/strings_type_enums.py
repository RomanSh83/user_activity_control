from enum import Enum


class StringsTypesEnum(str, Enum):
    ALARM = "alarm"
    COMMAND = "command"
    STAND_DOWN = "stand_down"
    TEMPLATES = "templates"


class TemplatesEnum(str, Enum):
    ALARM = "alarm_template"
    STAND_DOWN = "stand_down_template"
