from pathlib import Path
from typing import Any

from dishka import Provider, Scope, provide

from user_activity_control.bot_logic.schemas.category_schemas import CategoriesSchema
from user_activity_control.bot_logic.schemas.user_schemas import UsersSchema
from user_activity_control.infra.app_data.app_data import AppData
from user_activity_control.infra.logger.types import LoggerFactory


class AppDataProvider(Provider):
    @provide(scope=Scope.APP)
    def get_app_data(self, base_dir: Path, logger_factory: LoggerFactory) -> AppData:
        return AppData(base_dir=base_dir, logger_factory=logger_factory)

    @provide(scope=Scope.APP)
    def get_users(self, app_data: AppData) -> UsersSchema:
        return app_data.users

    @provide(scope=Scope.APP)
    def get_categories(self, app_data: AppData) -> CategoriesSchema:
        return app_data.categories

    @provide(scope=Scope.APP)
    def get_strings(self, app_data: AppData) -> dict[str, Any]:
        return app_data.strings
