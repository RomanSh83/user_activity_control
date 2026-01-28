import os
from typing import Any

import yaml

from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_base_settings
from user_activity_control.infra.locale.exceptions.locale_exceptions import (
    LocaleFormatArgumentsException,
    LocaleKeyException,
)


class LocaleUtils(Singleton):
    def __init__(self):
        self.locale_strings = self._get_locale_strings()

    @staticmethod
    def _get_locale_strings() -> dict[str, str]:
        lang = get_base_settings().LANGUAGE
        locale_file_path = os.path.join("locales", lang, "message_strings.yaml")

        with open(file=locale_file_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def translate(self, key: str, **kwargs: Any) -> str:
        try:
            locale_string = self.locale_strings[key]
        except KeyError:
            raise LocaleKeyException

        try:
            return locale_string.format(**kwargs)
        except KeyError:
            raise LocaleFormatArgumentsException


def get_translate_string(key: str, **kwargs: Any) -> str:
    return LocaleUtils().translate(key, **kwargs)
