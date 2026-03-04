from aiogram import Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent
from aiogram.utils.formatting import Bold, Pre, Text

from user_activity_control.infra.logger.types import LoggerFactory

exceptions_router = Router()


@exceptions_router.error()
async def exceptions_handler(event: ErrorEvent, state: FSMContext, admins: set[int], logger_factory: LoggerFactory):
    logger = logger_factory(__name__)
    logger.error("Error: %s", event.exception, exc_info=True)
    await state.clear()

    message_content = Text(
        Bold("Ошибка при работе бота!"), Text("\n\nПри работе бота произошла ошибка:"), Pre(str(event.exception))
    )
    for admin_id in admins:
        try:
            await event.update.bot.send_message(admin_id, **message_content.as_kwargs())
        except TelegramForbiddenError:
            logger.warning(
                f"Failed to send notification to admin {admin_id}: bot is blocked or conversation not started."
            )
