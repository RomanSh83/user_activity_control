from typing import Any

from user_activity_control.bot_logic.schemas.category_schemas import CategorySchema
from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_categories, get_config, get_logger


class CategoryService(Singleton):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.categories = get_categories()

    def _save_strings(self, category_slug: str, strings_data: dict[str, Any]) -> None:
        self.config.save_strings(category_slug=category_slug, strings_data=strings_data)

    def _rename_and_update_strings(
        self, old_category_slug: str, new_category_slug: str, strings_data: dict[str, Any]
    ) -> None:
        self.config.rename_and_update_strings(
            old_category_slug=old_category_slug, new_category_slug=new_category_slug, strings_data=strings_data
        )

    def get_categories(self, offset: int, limit: int) -> list[CategorySchema]:
        categories_keys = sorted(self.categories.keys())
        current_categories_keys = (
            categories_keys[offset:]
            if offset + limit - 1 > len(self.categories)
            else categories_keys[offset : offset + limit]
        )
        return [self.get_category(category_slug=key) for key in current_categories_keys]

    def get_category(self, category_slug: str) -> CategorySchema:
        return CategorySchema(slug=category_slug, name=self.categories[category_slug]["name"])

    def exists_category(self, category_slug: str) -> bool:
        return category_slug in self.categories

    def create_category(self, category_data: CategorySchema, strings_data: dict[str, Any]) -> None:
        self.config.save_category(category_data=category_data)
        self._save_strings(category_slug=category_data.slug, strings_data=strings_data)

    def update_category(self, category_slug: str, category_data: CategorySchema, strings_data: dict[str, Any]) -> None:
        if category_data.slug == category_slug:
            self.config.save_category(category_data=category_data)
            self._save_strings(category_slug=category_data.slug, strings_data=strings_data)
        else:
            self.config.remove_category(category_slug=category_slug)
            self.config.save_category(category_data=category_data)
            self._rename_and_update_strings(
                old_category_slug=category_slug, new_category_slug=category_data.slug, strings_data=strings_data
            )

    def remove_category(self, category_slug: str) -> None:
        self.config.remove_category(category_slug=category_slug)
        self.config.remove_strings(category_slug=category_slug)
