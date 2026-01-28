from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from user_activity_control.bot_logic.enums.command_enums import ChatCommandEnum
from user_activity_control.bot_logic.filters.chat_user_filters import ChatUserFilter
from user_activity_control.bot_logic.schemas.control_user_schemas import ControlUserSchema
from user_activity_control.bot_logic.services.user_activity_service import UserActivityService
from user_activity_control.core.config import get_logger
from user_activity_control.infra.locale.types import Locale

chat_command_router = Router()
logger = get_logger(__name__)


@chat_command_router.message(Command(ChatCommandEnum.ABOUT), ChatUserFilter())
async def unique_chat_about_handler(
    message: Message, _: Locale, user_activity_service: UserActivityService, control_user: ControlUserSchema
) -> None:
    if not control_user.unique_command_reactions:
        await message.answer(_("command_chat_about"))
        return
    await user_activity_service.proceed_activity(message=message, control_user=control_user, is_command=True)


@chat_command_router.message(Command(ChatCommandEnum.ABOUT))
async def common_chat_about_handler(message: Message, _: Locale) -> None:
    await message.answer(_("command_chat_about"))
