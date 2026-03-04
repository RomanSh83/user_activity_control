from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka import FromDishka

from user_activity_control.bot_logic.callback_classes.common_menu_callbacks import (
    ExitMenuCallbackFactory,
    NoopCallbackFactory,
)
from user_activity_control.infra.locale.types import LocaleFactory
from user_activity_control.infra.telegram.bot_services.message_service import MessageService
from user_activity_control.infra.telegram.bot_services.state_services import StateService

menu_router = Router()


@menu_router.callback_query(NoopCallbackFactory.filter())
async def categories_handler(callback: CallbackQuery) -> None:
    await callback.answer()


@menu_router.callback_query(ExitMenuCallbackFactory().filter())
async def exit_handler(
    callback: CallbackQuery,
    state: FSMContext,
    message_service: FromDishka[MessageService],
    state_service: FromDishka[StateService],
    _: FromDishka[LocaleFactory],
) -> None:
    await callback.answer()
    await state_service.safe_clear(state=state)

    await message_service.send_message(event=callback, state=state, text=_("menu_exit"))
