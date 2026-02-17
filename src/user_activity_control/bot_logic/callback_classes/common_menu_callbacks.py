from aiogram.filters.callback_data import CallbackData

from user_activity_control.bot_logic.enums.menu_enums import MenuActionEnum


class NavigatorCallbackFactory(CallbackData, prefix="navigator"):  # type: ignore
    entity: str
    page: int
    total: int
    from_action: MenuActionEnum | None = None


class AdminMenuCallbackFactory(CallbackData, prefix="admin_menu"):  # type: ignore
    pass


class ExitMenuCallbackFactory(CallbackData, prefix="exit_menu"):  # type: ignore
    pass


class SkipMenuCallbackFactory(CallbackData, prefix="skip_menu"):  # type: ignore
    pass


class NoopCallbackFactory(CallbackData, prefix="noop_menu"):  # type: ignore
    pass


class ConfirmMenuCallbackFactory(CallbackData, prefix="confirm_menu"):  # type: ignore
    pass
