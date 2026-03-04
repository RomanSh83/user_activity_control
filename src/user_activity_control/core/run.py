from aiogram import Bot, Dispatcher
from dishka.integrations.aiogram import setup_dishka

from user_activity_control.bot_logic.handlers import main_router
from user_activity_control.core.config import Config
from user_activity_control.core.di.di import get_di_container
from user_activity_control.infra.locale.types import LocaleFactory
from user_activity_control.infra.logger.project_logger import ProjectLogger
from user_activity_control.infra.logger.types import LoggerFactory


async def run_app(config: Config, project_logger: ProjectLogger) -> None:
    container = get_di_container(config=config, project_logger=project_logger)

    try:
        dp = await container.get(Dispatcher)
        bot = await container.get(Bot)

        dp.include_router(main_router)

        setup_dishka(container=container, router=dp, auto_inject=True)

        async with bot:
            await dp.start_polling(
                bot,
                logger_factory=await container.get(LoggerFactory),
                admins=await container.get(set[str]),
                _=await container.get(LocaleFactory),
            )
    finally:
        await container.close()
