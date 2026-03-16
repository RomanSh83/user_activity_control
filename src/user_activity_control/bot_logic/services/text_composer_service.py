import random
from pathlib import Path

from user_activity_control.bot_logic.enums.strings_type_enums import StringsTypesEnum
from user_activity_control.bot_logic.schemas.strings_schemas import StringsCollectionSchema
from user_activity_control.bot_logic.schemas.user_schemas import UserSchema
from user_activity_control.core.enums.enums import ProjectFoldersEnum
from user_activity_control.infra.logger.types import LoggerFactory


class TextComposerService:
    def __init__(self, base_dir: Path, logger_factory: LoggerFactory, strings: StringsCollectionSchema):
        self.logger = logger_factory(__name__)
        self.strings_dir = base_dir / ProjectFoldersEnum.APP_DATA / ProjectFoldersEnum.STRINGS
        self.strings = strings

    def compose_text(self, user: UserSchema, string_type: StringsTypesEnum) -> str | None:
        category = user.category

        if category not in self.strings.root:
            return None

        current_strings = getattr(self.strings.root[category], string_type, [])
        templates = getattr(self.strings.root[category], StringsTypesEnum.TEMPLATES, {})

        if len(current_strings) == 0:
            return None

        text_body = random.choice(current_strings)

        if string_type == StringsTypesEnum.COMMAND:
            return text_body

        template = templates.get(f"{string_type.value}_template")

        if not template:
            return None

        return template.format(text_body=text_body)
