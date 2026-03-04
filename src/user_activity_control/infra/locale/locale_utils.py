from pathlib import Path
from typing import Any

import yaml
from dynaconf import Dynaconf

from user_activity_control.infra.locale.exceptions.locale_exceptions import (
    LocaleFormatArgumentsException,
    LocaleKeyException,
)


class LocaleUtils:
    def __init__(self, base_dir: Path, settings: Dynaconf):
        self.locale_dir = base_dir / "locales" / settings.LANGUAGE
        self.locale_strings = self._get_locale_strings()

    def _get_locale_strings(self) -> dict[str, str]:
        locale_file_path = self.locale_dir / "message_strings.yaml"

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

        for k, v in kwargs.items():
            if isinstance(v, bool):
                kwargs[k] = self._proceed_bool_value(key=k, value=v)

        try:
            return locale_string.format(**kwargs)
        except KeyError:
            raise LocaleFormatArgumentsException
