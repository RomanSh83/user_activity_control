import shutil
from logging import Logger
from pathlib import Path
from typing import Any

import yaml
from dynaconf import Dynaconf

from user_activity_control.bot_logic.enums.entity_enums import UserSettingsEnum
from user_activity_control.bot_logic.schemas.category_schemas import CategorySchema
from user_activity_control.bot_logic.schemas.user_schemas import UserSchema, UserUpdateSchema
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

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        self.categories = self._get_categories()
        self.user_settings = self._get_user_settings()
        self.strings = self._get_strings()
        self._clear_app_data_strings()
        self._initialized = True

    def _get_categories(self) -> dict[str, dict[str, Any]]:
        file_data = self._load_data_from_yaml(file_path=(self.users_config_dir / "categories.yaml"))
        return file_data if isinstance(file_data, dict) else {}

    def _get_user_settings(self) -> dict[str, dict[str, Any]]:
        file_data = self._load_data_from_yaml(file_path=(self.users_config_dir / "users_settings.yaml"))
        return file_data if isinstance(file_data, dict) else {}

    def _get_strings(self) -> dict[str, Any]:
        strings: dict[str, dict[str, Any]] = {}
        for category in self.categories.keys():
            strings[category] = {}
            yaml_dir = self.strings_dir / category
            yaml_files = yaml_dir.glob("*.yaml")
            for yaml_file in yaml_files:
                key = yaml_file.stem
                strings[category][key] = self._load_data_from_yaml(file_path=yaml_file)
        return strings

    def _clear_app_data_strings(self) -> None:
        if self.strings_dir.exists():
            removing_dirs = {d for d in self.strings_dir.iterdir() if d.is_dir() and d.name not in self.strings}
            for removing_dir in removing_dirs:
                shutil.rmtree(removing_dir, ignore_errors=True)

    @staticmethod
    def _load_data_from_yaml(file_path: Path) -> Any:
        if not file_path.exists():
            return None
        with open(file=file_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def _save_to_yaml(file_path: Path, file_data: Any) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file=file_path, mode="w", encoding="utf-8") as f:
            yaml.dump(file_data, f, allow_unicode=True)

    def _save_strings_to_yaml(self, category_slug: str) -> None:
        for key in self.strings[category_slug]:
            self._save_to_yaml(
                file_path=(self.strings_dir / category_slug / f"{key}.yaml"), file_data=self.strings[category_slug][key]
            )

    def save_category(self, category_data: CategorySchema) -> None:
        self.categories[category_data.slug] = {"name": category_data.name}
        self._save_to_yaml(file_path=(self.users_config_dir / "categories.yaml"), file_data=self.categories)

    def remove_category(self, category_slug: str) -> None:
        self.categories.pop(category_slug, None)
        self._save_to_yaml(file_path=(self.users_config_dir / "categories.yaml"), file_data=self.categories)

    def rename_and_update_strings(
        self, old_category_slug: str, new_category_slug: str, strings_data: dict[str, Any]
    ) -> None:
        current_strings = self.strings.pop(old_category_slug)
        current_strings.update(strings_data)
        self.strings[new_category_slug] = current_strings
        self._save_strings_to_yaml(category_slug=new_category_slug)
        self.remove_strings(category_slug=old_category_slug)

    def remove_strings(self, category_slug: str) -> None:
        removing_dir = self.strings_dir / category_slug
        shutil.rmtree(removing_dir, ignore_errors=True)

    def save_strings(self, category_slug: str, strings_data: dict[str, Any]) -> None:
        self.strings[category_slug] = strings_data
        self._save_strings_to_yaml(category_slug=category_slug)

    def save_user(self, user: UserSchema) -> None:
        user_data = user.model_dump()
        user_id = user_data.pop(UserSettingsEnum.USER_ID)
        self.user_settings[user_id] = user_data
        self._save_to_yaml(file_path=(self.users_config_dir / "users_settings.yaml"), file_data=self.user_settings)

    def update_user(self, user_id: str, user_data: UserUpdateSchema) -> None:
        user_update_data = user_data.model_dump(exclude_none=True)
        if not user_update_data:
            return
        self.user_settings[user_id].update(user_update_data)
        self._save_to_yaml(file_path=(self.users_config_dir / "users_settings.yaml"), file_data=self.user_settings)

    def remove_user(self, user_id: str) -> None:
        self.user_settings.pop(user_id, None)
        self._save_to_yaml(file_path=(self.users_config_dir / "users_settings.yaml"), file_data=self.user_settings)

    def remove_users(self, user_ids: list[str]) -> None:
        for user_id in user_ids:
            self.user_settings.pop(user_id, None)
        self._save_to_yaml(file_path=(self.users_config_dir / "users_settings.yaml"), file_data=self.user_settings)


def get_config() -> Config:
    return Config()


def get_settings() -> Dynaconf:
    return Config.settings


def get_base_dir() -> Path:
    return Config.base_dir


def get_user_settings() -> dict[str, dict[str, Any]]:
    return Config().user_settings


def get_categories() -> dict[str, dict[str, Any]]:
    return Config().categories


def get_strings() -> dict[str, Any]:
    return Config().strings


def get_admins() -> set[int]:
    return Config.admins


def get_logger(name: str | None = None) -> Logger:
    if not name:
        name = __name__
    return Config.logger.get_logger(name=name)
