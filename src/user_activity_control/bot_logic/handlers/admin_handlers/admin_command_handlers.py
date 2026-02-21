from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from user_activity_control.bot_logic.callback_classes.common_menu_callbacks import AdminMenuCallbackFactory
from user_activity_control.bot_logic.enums.command_enums import AdminCommandEnum
from user_activity_control.bot_logic.filters.permission_filters import AdminFilter
from user_activity_control.bot_logic.keyboards.keyboard_generator import KeyboardGenerator
from user_activity_control.bot_logic.services.bot_services.send_message_service import MessageService
from user_activity_control.bot_logic.services.bot_services.state_services import StateService
from user_activity_control.core.config import get_logger
from user_activity_control.infra.locale.types import Locale

admin_command_router = Router()
admin_command_router.message.filter(AdminFilter(), F.chat.type == "private")

logger = get_logger(__name__)


@admin_command_router.message(Command(AdminCommandEnum.ABOUT))
async def admin_about_handler(message: Message, message_service: MessageService, state: FSMContext, _: Locale) -> None:
    await message_service.send_message(event=message, state=state, text=_("command_admin_about"))


@admin_command_router.message(Command(AdminCommandEnum.START))
@admin_command_router.callback_query(AdminMenuCallbackFactory.filter())
async def admin_start_handler(
    event: Message | CallbackQuery,
    message_service: MessageService,
    state_service: StateService,
    state: FSMContext,
    keyboard_generator: KeyboardGenerator,
    _: Locale,
) -> None:
    await state_service.safe_clear(state=state)
    await state_service.push_current_callback(state=state, callback_data=AdminMenuCallbackFactory())

    kb = keyboard_generator.get_admin_keyboard()
    await message_service.send_message(event=event, state=state, text=_("command_admin_start"), reply_markup=kb)
