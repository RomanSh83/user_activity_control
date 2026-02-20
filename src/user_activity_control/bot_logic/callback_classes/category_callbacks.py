from aiogram.filters.callback_data import CallbackData

from user_activity_control.bot_logic.enums.menu_enums import MenuActionEnum


class CategoryCallbackFactory(CallbackData, prefix="category"):  # type: ignore
    action: MenuActionEnum
    category_id: str | None = None
    page: int = 0
    total: int | None = None
