import shutil
from pathlib import Path
from typing import Any

import yaml

from user_activity_control.bot_logic.enums.entity_enums import CategoryEnum, UsersEnum
from user_activity_control.bot_logic.enums.strings_type_enums import StringsTypesEnum
from user_activity_control.bot_logic.schemas.category_schemas import (
    CategoriesSchema,
    CategoryParamsSchema,
    CategoryParamsUpdateSchema,
    CategorySchema,
)
from user_activity_control.bot_logic.schemas.strings_schemas import StringsCollectionSchema, StringsItemSchema
from user_activity_control.bot_logic.schemas.user_schemas import (
    UserParamsSchema,
    UserParamsUpdateSchema,
    UserSchema,
    UsersSchema,
)
from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.enums.enums import ProjectFoldersEnum, StringsFilesEnum, UsersConfigFilesEnum
from user_activity_control.infra.logger.types import LoggerFactory


class AppData(Singleton):
    def __init__(self, base_dir: Path, logger_factory: LoggerFactory):
        self._logger = logger_factory(__name__)
        self._base_dir = base_dir
        self._strings_dir = self._get_strings_dir()
        self._users_file_path = self._get_users_file_path()
        self._categories_file_path = self._get_categories_file_path()
        self.categories = self._get_categories()
        self.users = self._get_users()
        self.strings = self._get_strings()
        self._clear_app_data_strings()

    def _get_strings_dir(self) -> Path:
        return self._base_dir / ProjectFoldersEnum.APP_DATA / ProjectFoldersEnum.STRINGS

    def _get_categories_file_path(self) -> Path:
        return (
            self._base_dir
            / ProjectFoldersEnum.APP_DATA
            / ProjectFoldersEnum.USERS_CONFIG
            / UsersConfigFilesEnum.CATEGORIES
        )

    def _get_users_file_path(self) -> Path:
        return (
            self._base_dir / ProjectFoldersEnum.APP_DATA / ProjectFoldersEnum.USERS_CONFIG / UsersConfigFilesEnum.USERS
        )

    def _get_categories(self) -> CategoriesSchema:
        yaml_data = self._load_data_from_yaml(yaml_path=self._categories_file_path)
        categories_data = yaml_data if isinstance(yaml_data, dict) else {}
        sorted_categories_data = self._sort_categories_dict(categories_data)
        return CategoriesSchema.model_validate(sorted_categories_data)

    def _get_users(self) -> UsersSchema:
        yaml_data = self._load_data_from_yaml(yaml_path=self._users_file_path)
        users_data = yaml_data if isinstance(yaml_data, dict) else {}
        sorted_users_data = self._sort_users_dict(users_data)
        return UsersSchema.model_validate(sorted_users_data)

    def _get_strings(self) -> StringsCollectionSchema:
        strings: dict[str, Any] = {}
        for category_id in self.categories.root.keys():
            strings[category_id] = {}
            strings_item_dir = self._strings_dir / category_id
            for strings_file in StringsFilesEnum:
                yaml_path = strings_item_dir / strings_file
                strings_name = yaml_path.stem
                yaml_data = self._load_data_from_yaml(yaml_path=yaml_path)
                expected_type = dict if strings_file == StringsFilesEnum.TEMPLATES else list
                if not isinstance(yaml_data, expected_type) or len(yaml_data) == 0:
                    self._logger.warning(
                        f"File {strings_file.value} for category ID: {category_id} contains incorrect data."
                    )
                    yaml_data = expected_type()
                strings[category_id][strings_name] = yaml_data
        return StringsCollectionSchema.model_validate(strings)

    def _clear_app_data_strings(self) -> None:
        if self._strings_dir.exists():
            removing_dirs = {d for d in self._strings_dir.iterdir() if d.is_dir() and d.name not in self.strings.root}
            for removing_dir in removing_dirs:
                shutil.rmtree(removing_dir, ignore_errors=True)

    @staticmethod
    def _load_data_from_yaml(yaml_path: Path) -> Any:
        if not yaml_path.exists():
            return None
        with open(file=yaml_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def _save_to_yaml(yaml_path: Path, yaml_data: Any) -> None:
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file=yaml_path, mode="w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False)

    def _save_strings_to_yaml(self, category_id: str) -> None:
        for strings_name in StringsTypesEnum:
            yaml_data = getattr(self.strings.root[category_id], strings_name)
            if yaml_data:
                self._save_to_yaml(
                    yaml_path=(self._strings_dir / category_id / f"{strings_name.value}.yaml"),
                    yaml_data=yaml_data,
                )

    def _sort_categories(self) -> None:
        sorted_categories = sorted(self.categories.root.items(), key=lambda item: item[1].name)
        self.categories.root = dict(sorted_categories)

    def _sort_users(self) -> None:
        sorted_users = sorted(self.users.root.items(), key=lambda item: item[0])
        self.users.root = dict(sorted_users)

    def _sort_categories_dict(self, categories_dict: dict[str, Any]) -> dict[str, Any]:
        return dict(sorted(categories_dict.items(), key=lambda item: item[1].get(CategoryEnum.NAME)))

    def _sort_users_dict(self, users_dict: dict[str, Any]) -> dict[str, Any]:
        return dict(sorted(users_dict.items(), key=lambda item: item[0]))

    def _sort_and_save_categories(self) -> None:
        self._sort_categories()
        self._save_categories_to_yaml()

    def _save_categories_to_yaml(self) -> None:
        self._save_to_yaml(yaml_path=self._categories_file_path, yaml_data=self.categories.model_dump())

    def _sort_and_save_users(self) -> None:
        self._sort_users()
        self._save_users_to_yaml()

    def _save_users_to_yaml(self) -> None:
        self._save_to_yaml(yaml_path=self._users_file_path, yaml_data=self.users.model_dump())

    def save_category(self, category: CategorySchema) -> None:
        category_data = category.model_dump()
        category_id = category_data.pop(CategoryEnum.CATEGORY_ID)
        self.categories.root[category_id] = CategoryParamsSchema.model_validate(category_data)
        self._sort_and_save_categories()

    def update_category(self, category_id: str, category_data: CategoryParamsUpdateSchema) -> None:
        category_update_data = category_data.model_dump(exclude_none=True)
        if not category_update_data:
            return
        for key, value in category_update_data.items():
            setattr(self.categories.root[category_id], key, value)
        self._sort_and_save_categories()

    def remove_category(self, category_id: str) -> None:
        self.categories.root.pop(category_id, None)
        self._save_categories_to_yaml()

    def update_strings(self, category_id: str, strings_data: StringsItemSchema) -> None:
        strings_update_data = strings_data.model_dump(exclude_none=True)
        if not strings_update_data:
            return
        for key, value in strings_update_data.items():
            setattr(self.strings.root[category_id], key, value)
        self._save_strings_to_yaml(category_id=category_id)

    def remove_strings(self, category_id: str) -> None:
        self.strings.root.pop(category_id)
        removing_dir = self._strings_dir / category_id
        shutil.rmtree(removing_dir, ignore_errors=True)

    def save_strings(self, category_id: str, strings_data: StringsItemSchema) -> None:
        self.strings.root[category_id] = strings_data
        self._save_strings_to_yaml(category_id=category_id)

    def save_user(self, user: UserSchema) -> None:
        user_data = user.model_dump()
        user_id = user_data.pop(UsersEnum.USER_ID)
        self.users.root[user_id] = UserParamsSchema.model_validate(user_data)
        self._sort_and_save_users()

    def update_user(self, user_id: str, user_data: UserParamsUpdateSchema) -> None:
        user_update_data = user_data.model_dump(exclude_none=True)
        if not user_update_data:
            return
        for key, value in user_update_data.items():
            setattr(self.users.root[user_id], key, value)
        self._save_users_to_yaml()

    def remove_user(self, user_id: str) -> None:
        self.users.root.pop(user_id, None)
        self._save_users_to_yaml()

    def remove_users(self, user_ids: list[str]) -> None:
        for user_id in user_ids:
            self.users.root.pop(user_id, None)
        self._save_users_to_yaml()
