from logging import Logger
from pathlib import Path
from typing import Any

import yaml
from dynaconf import Dynaconf

from user_activity_control.core.base.singleton import Singleton
from user_activity_control.infra.logger.project_logger import ProjectLogger


class Config(Singleton):
    base_dir = Path(__file__).resolve().parents[3]
    config_dir = base_dir / "config"
    base_settings = Dynaconf(
        root_path=base_dir, environments=True, envvar_prefix="", settings_files=[(config_dir / "base_settings.yaml")]
    )
    logger = ProjectLogger(base_dir=base_dir, settings=base_settings)
    admins = set(base_settings.ADMIN_IDS)

    def __init__(self) -> None:
        self.user_types = self._get_user_types()
        self.user_settings = self._get_user_settings()

    def _get_user_types(self) -> set[str]:
        file_data = self._load_data_from_yaml(file_path=(self.config_dir / "user_types.yaml"))
        return set(file_data) if isinstance(file_data, list) else set()

    def _get_user_settings(self) -> dict[str, dict[str, Any]]:
        file_data = self._load_data_from_yaml(file_path=(self.config_dir / "users_settings.yaml"))
        return file_data if isinstance(file_data, dict) else {}

    def _load_data_from_yaml(self, file_path: Path) -> Any:
        if not file_path.exists():
            return None
        with open(file=file_path, encoding="utf-8") as f:
            return yaml.safe_load(f)


def get_base_settings() -> Dynaconf:
    return Config.base_settings


def get_base_dir() -> Path:
    return Config.base_dir


def get_user_settings() -> dict[str, dict[str, Any]]:
    return Config().user_settings


def get_user_types() -> set[str]:
    return Config().user_types


def get_admins() -> set[int]:
    return Config.admins


def get_logger(name: str | None = None) -> Logger:
    if not name:
        name = __name__
    return Config.logger.get_logger(name=name)
