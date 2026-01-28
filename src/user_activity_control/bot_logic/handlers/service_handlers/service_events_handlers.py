from aiogram import Bot, Router
from aiogram.exceptions import TelegramForbiddenError

from user_activity_control.bot_logic.commands.commands import set_commands
from user_activity_control.core.config import get_logger
from user_activity_control.infra.locale.types import Locale

events_router = Router()
logger = get_logger(__name__)


@events_router.startup()
async def start_bot(bot: Bot, _: Locale, admins: set[str]) -> None:
    logger.info("Starting bot")
    await set_commands(bot=bot, _=_)
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, _("service_bot_started"))
        except TelegramForbiddenError:
            logger.warning(
                f"Failed to send notification to admin {admin_id}: bot is blocked or conversation not started."
            )


@events_router.shutdown()
async def stop_bot(bot: Bot, _: Locale, admins: set[str]):
    logger.info("Stopping bot")
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, _("service_bot_stopped"))
        except TelegramForbiddenError:
            logger.warning(
                f"Failed to send notification to admin {admin_id}: bot is blocked or conversation not started."
            )
