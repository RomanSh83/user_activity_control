from aiogram import Bot, Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent

from user_activity_control.core.config import get_logger

exceptions_router = Router()
logger = get_logger(__name__)


@exceptions_router.error()
async def exceptions_handler(event: ErrorEvent, bot: Bot, admins: set[int], state: FSMContext):
    logger.error("Error: %s", event.exception, exc_info=True)
    await state.clear()

    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f"Error: {event.exception}")
        except TelegramForbiddenError:
            logger.warning(
                f"Failed to send notification to admin {admin_id}: bot is blocked or conversation not started."
            )
