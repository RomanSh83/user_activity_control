from aiogram import Router
from aiogram.types import CallbackQuery, Message

from user_activity_control.bot_logic.filters.chat_user_filters import ChatUserFilter
from user_activity_control.bot_logic.schemas.control_user_schemas import ControlUserSchema
from user_activity_control.bot_logic.services.user_activity_service import UserActivityService
from user_activity_control.core.config import get_logger

chat_activity_router = Router()
logger = get_logger(__name__)


@chat_activity_router.message(ChatUserFilter())
@chat_activity_router.callback_query(ChatUserFilter())
@chat_activity_router.edited_message(ChatUserFilter())
async def user_activity_handler(
    event: Message | CallbackQuery,
    user_activity_service: UserActivityService,
    control_user: ControlUserSchema,
) -> None:
    message = event
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()

    await user_activity_service.proceed_activity(message=message, control_user=control_user)
