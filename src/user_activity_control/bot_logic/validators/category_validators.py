import re

import yaml
from aiogram.exceptions import DetailedAiogramError
from aiogram.types import Message

from user_activity_control.bot_logic.enums.strings_type_enums import TemplatesEnum
from user_activity_control.bot_logic.services.admin_services.categories_services import CategoryService
from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_logger, get_settings
from user_activity_control.infra.locale.locale_utils import get_translate_string


class CategoryValidator(Singleton):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.settings = get_settings()
        self.category_service = CategoryService()
        self._ = get_translate_string

    async def validate_name(self, value: str) -> tuple[None, str] | tuple[str, None]:
        if len(value) > get_settings().MAX_CATEGORY_NAME_LENGTH:
            return (
                None,
                self._("validator_category_name_length", max_length=get_settings().MAX_CATEGORY_NAME_LENGTH),
            )
        if not re.fullmatch(pattern="^[a-zA-Zа-яА-ЯёЁ0-9 ]+$", string=value):
            return None, self._("validator_category_name_regex")
        if self.category_service.exists_category_name(category_name=value.capitalize()):
            return None, self._("validator_category_name_exists")
        return value.capitalize(), None

    async def validate_yaml_file(self, message: Message) -> tuple[None, str] | tuple[dict | list, None]:
        if not message.document:
            return None, self._("validator_file_not_document")
        if message.document.file_size > self.settings.MAX_YAML_FILESIZE * 1024 * 1024:
            return None, self._("validator_file_too_big", max_file_size=self.settings.MAX_YAML_FILESIZE)
        try:
            file = await message.bot.get_file(message.document.file_id)
            file_stream = await message.bot.download_file(file.file_path)

            try:
                content_string = file_stream.read().decode("utf-8")
            except UnicodeDecodeError:
                return None, self._("validator_file_invalid_encoding")

            try:
                yaml_content = yaml.safe_load(content_string)
                return yaml_content, None
            except yaml.YAMLError:
                return None, self._("validator_file_yaml_error")

        except DetailedAiogramError:
            return None, self._("validator_file_upload_error")

    async def validate_templates_file(self, message: Message) -> tuple[None, str] | tuple[dict, None]:
        yaml_content, validate_error_text = await self.validate_yaml_file(message=message)

        if validate_error_text:
            return None, validate_error_text

        if not isinstance(yaml_content, dict):
            return None, self._("validator_templates_file_invalid_structure")

        for template in TemplatesEnum:
            if template.value not in yaml_content:
                return None, self._("validator_templates_missing_required_key", template=template.value)

        return yaml_content, None

    async def validate_strings_file(self, message: Message) -> tuple[None, str] | tuple[list, None]:
        yaml_content, validate_error_text = await self.validate_yaml_file(message=message)

        if validate_error_text:
            return None, validate_error_text

        if not isinstance(yaml_content, list):
            return None, self._("validator_strings_file_invalid_structure")

        return yaml_content, None
