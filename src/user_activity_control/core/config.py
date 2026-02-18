from logging import Logger
from pathlib import Path

from dynaconf import Dynaconf

from user_activity_control.core.base.singleton import Singleton
from user_activity_control.infra.logger.project_logger import ProjectLogger


class Config(Singleton):
    base_dir = Path(__file__).resolve().parents[3]
    users_config_dir = base_dir / "app_data" / "users_config"
    strings_dir = base_dir / "app_data" / "strings"

    settings = Dynaconf(
        root_path=base_dir,
        environments=True,
        envvar_prefix="",
        settings_files=[(base_dir / "config" / "settings.yaml")],
    )
    logger = ProjectLogger(base_dir=base_dir, settings=settings)
    admins = set(settings.ADMIN_IDS)


def get_config() -> Config:
    return Config()


def get_settings() -> Dynaconf:
    return Config.settings


def get_base_dir() -> Path:
    return Config.base_dir


def get_admins() -> set[int]:
    return Config.admins


def get_logger(name: str | None = None) -> Logger:
    if not name:
        name = __name__
    return Config.logger.get_logger(name=name)
