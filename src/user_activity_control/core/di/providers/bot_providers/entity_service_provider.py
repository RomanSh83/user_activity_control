from dishka import Provider, Scope, provide

from user_activity_control.bot_logic.schemas.category_schemas import CategoriesSchema
from user_activity_control.bot_logic.schemas.user_schemas import UsersSchema
from user_activity_control.bot_logic.services.category_services import CategoryService
from user_activity_control.bot_logic.services.user_services import UserService
from user_activity_control.infra.app_data.app_data import AppData
from user_activity_control.infra.logger.types import LoggerFactory


class EntityServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def get_category_service(
        self, app_data: AppData, categories: CategoriesSchema, logger_factory: LoggerFactory
    ) -> CategoryService:
        return CategoryService(app_data=app_data, categories=categories, logger_factory=logger_factory)

    @provide(scope=Scope.APP)
    def get_user_service(self, app_data: AppData, users: UsersSchema, logger_factory: LoggerFactory) -> UserService:
        return UserService(app_data=app_data, users=users, logger_factory=logger_factory)
