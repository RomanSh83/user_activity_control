import random
from typing import Any

import yaml

from user_activity_control.bot_logic.enums.strings_type_enums import StringsTypesEnum
from user_activity_control.bot_logic.schemas.control_user_schemas import ControlUserSchema
from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_base_dir, get_logger, get_user_types

logger = get_logger(__name__)


class TextComposerService(Singleton):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.user_types = get_user_types()
        self.strings_dir = get_base_dir() / "app_data" / "strings"
        self.strings = self._get_strings()

    def _get_strings(self) -> dict[str, Any]:
        strings: dict[Any, Any] = {}
        for user_type in self.user_types:
            strings[user_type] = {}
            yaml_dir = self.strings_dir / user_type
            yaml_files = yaml_dir.glob("*.yaml")
            for yaml_file in yaml_files:
                key = yaml_file.stem
                with open(file=yaml_file, encoding="utf-8") as f:
                    strings[user_type][key] = yaml.safe_load(f)
        return strings

    def compose_text(self, control_user: ControlUserSchema, string_type: str) -> str | None:
        user_type = control_user.type

        if (
            user_type not in self.strings
            or string_type not in self.strings[user_type]
            or len(self.strings[user_type][string_type]) == 0
        ):
            return None

        text_body = random.choice(self.strings[user_type][string_type])

        if string_type == StringsTypesEnum.COMMAND:
            return text_body

        if (
            "templates" not in self.strings[user_type]
            or f"{string_type}_template" not in self.strings[user_type]["templates"]
        ):
            return None

        template = self.strings[user_type]["templates"][f"{string_type}_template"]
        return template.format(text_body=text_body)
