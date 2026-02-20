from typing import Any

from user_activity_control.bot_logic.schemas.category_schemas import CategoryParamsUpdateSchema, CategorySchema
from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_logger
from user_activity_control.infra.app_data.app_data import get_app_data, get_categories


class CategoryService(Singleton):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.app_data = get_app_data()
        self.categories = get_categories()

    def _save_strings(self, category_id: str, strings_data: dict[str, Any]) -> None:
        self.app_data.save_strings(category_id=category_id, strings_data=strings_data)

    def _update_strings(self, category_id: str, strings_data: dict[str, Any]) -> None:
        self.app_data.update_strings(category_id=category_id, strings_data=strings_data)

    def get_categories(self, offset: int, limit: int) -> list[CategorySchema]:
        categories_keys = list(self.categories.root.keys())
        return [self.get_category(category_id=key) for key in categories_keys[offset : offset + limit]]

    def get_category(self, category_id: str) -> CategorySchema:
        return CategorySchema(category_id=category_id, name=self.categories.root[category_id].name)

    def exists_category_name(self, category_name: str) -> bool:
        for category in self.categories.root.values():
            if category.name == category_name:
                return True
        return False

    def create_category(self, category: CategorySchema, strings_data: dict[str, Any]) -> None:
        self.app_data.save_category(category=category)
        self._save_strings(category_id=category.category_id, strings_data=strings_data)

    def update_category(
        self, category_id: str, category_data: CategoryParamsUpdateSchema, strings_data: dict[str, Any]
    ) -> None:
        self.app_data.update_category(category_id=category_id, category_data=category_data)
        self._update_strings(category_id=category_id, strings_data=strings_data)

    def remove_category(self, category_id: str) -> None:
        self.app_data.remove_category(category_id=category_id)
        self.app_data.remove_strings(category_id=category_id)
