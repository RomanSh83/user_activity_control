from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from user_activity_control.bot_logic.callback_classes.common_menu_callbacks import (
    ExitMenuCallbackFactory,
    NoopCallbackFactory,
)
from user_activity_control.bot_logic.services.bot_services.send_message_service import MessageService
from user_activity_control.bot_logic.services.bot_services.state_services import StateService
from user_activity_control.infra.locale.types import Locale

menu_router = Router()


@menu_router.callback_query(NoopCallbackFactory.filter())
async def categories_handler(callback: CallbackQuery) -> None:
    await callback.answer()


@menu_router.callback_query(ExitMenuCallbackFactory().filter())
async def exit_handler(
    callback: CallbackQuery, message_service: MessageService, state_service: StateService, state: FSMContext, _: Locale
) -> None:
    await callback.answer()
    await state_service.safe_clear(state=state)

    await message_service.send_message(event=callback, state=state, text=_("menu_exit"))
