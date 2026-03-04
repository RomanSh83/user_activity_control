from pathlib import Path

from dishka import Provider, Scope, provide
from dynaconf import Dynaconf

from user_activity_control.core.config import Config


class ConfigProvider(Provider):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config

    @provide(scope=Scope.APP)
    def get_settings(self) -> Dynaconf:
        return self.config.settings

    @provide(scope=Scope.APP)
    def get_base_dir(self) -> Path:
        return self.config.base_dir

    @provide(scope=Scope.APP)
    def get_admins(self, settings: Dynaconf) -> set[str]:
        return set(settings.ADMIN_IDS)
