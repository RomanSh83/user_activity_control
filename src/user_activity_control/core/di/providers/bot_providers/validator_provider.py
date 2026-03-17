from dishka import Provider, Scope, provide
from dynaconf import Dynaconf

from user_activity_control.bot_logic.services.category_services import CategoryService
from user_activity_control.bot_logic.services.user_services import UserService
from user_activity_control.bot_logic.validators.category_validators import CategoryValidator
from user_activity_control.bot_logic.validators.user_validators import UserValidator
from user_activity_control.infra.locale.types import LocaleFactory
from user_activity_control.infra.logger.types import LoggerFactory


class ValidatorProvider(Provider):
    @provide(scope=Scope.APP)
    def get_category_validator(
        self, logger_factory: LoggerFactory, settings: Dynaconf, category_service: CategoryService, _: LocaleFactory
    ) -> CategoryValidator:
        return CategoryValidator(
            logger_factory=logger_factory, settings=settings, category_service=category_service, _=_
        )

    @provide(scope=Scope.APP)
    def get_user_validator(
        self, logger_factory: LoggerFactory, user_service: UserService, _: LocaleFactory
    ) -> UserValidator:
        return UserValidator(logger_factory=logger_factory, user_service=user_service, _=_)
