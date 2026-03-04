import random
from pathlib import Path
from typing import Any

from user_activity_control.bot_logic.enums.strings_type_enums import StringsTypesEnum
from user_activity_control.bot_logic.schemas.category_schemas import CategoriesSchema
from user_activity_control.bot_logic.schemas.control_user_schemas import ControlUserSchema
from user_activity_control.core.enums.enums import ProjectFoldersEnum
from user_activity_control.infra.logger.types import LoggerFactory


class TextComposerService:
    def __init__(
        self, categories: CategoriesSchema, base_dir: Path, logger_factory: LoggerFactory, strings: dict[str, Any]
    ):
        self.logger = logger_factory(__name__)
        self.categories = categories
        self.strings_dir = base_dir / ProjectFoldersEnum.APP_DATA / ProjectFoldersEnum.STRINGS
        self.strings = strings

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
