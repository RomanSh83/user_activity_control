from pathlib import Path
from typing import cast

from dishka import Provider, Scope, provide
from dynaconf import Dynaconf

from user_activity_control.infra.locale.locale_utils import LocaleUtils
from user_activity_control.infra.locale.types import LocaleFactory


class LocaleProvider(Provider):
    @provide(scope=Scope.APP)
    def get_locale_utils(self, base_dir: Path, settings: Dynaconf) -> LocaleUtils:
        return LocaleUtils(base_dir=base_dir, settings=settings)

    @provide(scope=Scope.APP)
    def get_translate_string(self, locale_utils: LocaleUtils) -> LocaleFactory:
        return cast(LocaleFactory, locale_utils.translate)
