from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka

from user_activity_control.bot_logic.enums.command_enums import CommonCommandEnum
from user_activity_control.bot_logic.filters.chat_user_filters import ChatUserFilter
from user_activity_control.bot_logic.schemas.user_schemas import UserSchema
from user_activity_control.bot_logic.services.user_activity_service import UserActivityService
from user_activity_control.infra.locale.types import LocaleFactory

chat_command_router = Router()


@chat_command_router.message(
    Command(CommonCommandEnum.ABOUT), F.chat.type.in_({"group", "supergroup"}), ChatUserFilter()
)
async def unique_chat_about_handler(
    message: Message,
    user: UserSchema,
    user_activity_service: FromDishka[UserActivityService],
    _: FromDishka[LocaleFactory],
) -> None:
    if not user.unique_command_reactions:
        await message.answer(_("command_chat_about"))
        return
    await user_activity_service.proceed_activity(message=message, user=user, is_command=True)


@chat_command_router.message(Command(CommonCommandEnum.ABOUT), F.chat.type.in_({"group", "supergroup"}))
async def common_chat_about_handler(message: Message, _: FromDishka[LocaleFactory]) -> None:
    await message.answer(_("command_chat_about"))
