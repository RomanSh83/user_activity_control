from pathlib import Path

from dishka import Provider, Scope, provide

from user_activity_control.bot_logic.schemas.strings_schemas import StringsCollectionSchema
from user_activity_control.bot_logic.services.text_composer_service import TextComposerService
from user_activity_control.bot_logic.services.user_activity_service import UserActivityService
from user_activity_control.infra.logger.types import LoggerFactory
from user_activity_control.infra.storage.in_memory_storage import ActivityStorage


class AppServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def get_text_composer_service(
        self, base_dir: Path, logger_factory: LoggerFactory, strings: StringsCollectionSchema
    ) -> TextComposerService:
        return TextComposerService(base_dir=base_dir, strings=strings, logger_factory=logger_factory)

    @provide(scope=Scope.APP)
    def get_user_activity_service(
        self, storage: ActivityStorage, text_composer: TextComposerService, logger_factory: LoggerFactory
    ) -> UserActivityService:
        return UserActivityService(storage=storage, text_composer=text_composer, logger_factory=logger_factory)
