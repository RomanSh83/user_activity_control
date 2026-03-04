from dishka import AsyncContainer, make_async_container

from user_activity_control.core.config import Config
from user_activity_control.core.di.providers.bot_providers import (
    AppServiceProvider,
    EntityServiceProvider,
    KeyboardProvider,
    ValidatorProvider,
)
from user_activity_control.core.di.providers.infra_providers import (
    ActivityStorageProvider,
    AppDataProvider,
    BotProvider,
    BotServiceProvider,
    ConfigProvider,
    LocaleProvider,
    LoggerProvider,
)
from user_activity_control.infra.logger.project_logger import ProjectLogger


def get_di_container(config: Config, project_logger: ProjectLogger) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(config=config),
        LoggerProvider(project_logger=project_logger),
        AppDataProvider(),
        LocaleProvider(),
        ActivityStorageProvider(),
        BotProvider(),
        BotServiceProvider(),
        AppServiceProvider(),
        EntityServiceProvider(),
        KeyboardProvider(),
        ValidatorProvider(),
    )
