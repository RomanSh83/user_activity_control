from aiogram.filters.callback_data import CallbackData

from user_activity_control.bot_logic.enums.menu_enums import MenuActionEnum


class UserCallbackFactory(CallbackData, prefix="user"):  # type: ignore
    action: MenuActionEnum
    uid: str | None = None
    page: int = 0
    total: int | None = None
    by_previous_button: bool = False
    by_paginate_button: bool = False
