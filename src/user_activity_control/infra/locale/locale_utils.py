import os
from typing import Any

import yaml

from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_logger, get_settings
from user_activity_control.infra.locale.exceptions.locale_exceptions import (
    LocaleFormatArgumentsException,
    LocaleKeyException,
)

logger = get_logger(__name__)


class LocaleUtils(Singleton):
    def __init__(self):
        self.locale_strings = self._get_locale_strings()

    @staticmethod
    def _get_locale_strings() -> dict[str, str]:
        lang = get_settings().LANGUAGE
        locale_file_path = os.path.join("locales", lang, "message_strings.yaml")

        with open(file=locale_file_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _proceed_bool_value(self, key: str, value: bool) -> str:
        key_suffix = "_true" if value else "_false"
        if key + key_suffix in self.locale_strings:
            return self.locale_strings[key + key_suffix]
        return self.locale_strings[f"default_bool{key_suffix}"]

    def translate(self, key: str, **kwargs: Any) -> str:
        try:
            locale_string = self.locale_strings[key]
        except KeyError:
            raise LocaleKeyException

        for key, value in kwargs.items():
            if isinstance(value, bool):
                kwargs[key] = self._proceed_bool_value(key=key, value=value)

        try:
            return locale_string.format(**kwargs)
        except KeyError:
            raise LocaleFormatArgumentsException


def get_translate_string(key: str, **kwargs: Any) -> str:
    return LocaleUtils().translate(key, **kwargs)
