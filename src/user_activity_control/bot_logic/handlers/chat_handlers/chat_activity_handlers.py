from aiogram import Router
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from user_activity_control.bot_logic.filters.chat_user_filters import ChatUserFilter
from user_activity_control.bot_logic.schemas.user_schemas import UserSchema
from user_activity_control.bot_logic.services.user_activity_service import UserActivityService

chat_activity_router = Router()


@chat_activity_router.message(ChatUserFilter())
@chat_activity_router.callback_query(ChatUserFilter())
@chat_activity_router.edited_message(ChatUserFilter())
async def user_activity_handler(
    event: Message | CallbackQuery, user: UserSchema, user_activity_service: FromDishka[UserActivityService]
) -> None:
    message = event
    if isinstance(event, CallbackQuery):
        message = event.message
        await event.answer()

    await user_activity_service.proceed_activity(message=message, user=user)
