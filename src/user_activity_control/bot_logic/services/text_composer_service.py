import random

from user_activity_control.bot_logic.enums.strings_type_enums import StringsTypesEnum
from user_activity_control.bot_logic.schemas.control_user_schemas import ControlUserSchema
from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_base_dir, get_categories, get_logger, get_strings


class TextComposerService(Singleton):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.categories = get_categories()
        self.strings_dir = get_base_dir() / "app_data" / "strings"
        self.strings = get_strings()

    def compose_text(self, control_user: ControlUserSchema, string_type: str) -> str | None:
        category = control_user.category

        if (
            category not in self.strings
            or string_type not in self.strings[category]
            or len(self.strings[category][string_type]) == 0
        ):
            return None

        text_body = random.choice(self.strings[category][string_type])

        if string_type == StringsTypesEnum.COMMAND:
            return text_body

        if (
            "templates" not in self.strings[category]
            or f"{string_type}_template" not in self.strings[category]["templates"]
        ):
            return None

        template = self.strings[category]["templates"][f"{string_type}_template"]
        return template.format(text_body=text_body)
