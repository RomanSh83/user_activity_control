from aiogram.filters.callback_data import CallbackData


class AdminMenuCallbackFactory(CallbackData, prefix="admin_menu"):  # type: ignore
    pass


class ExitMenuCallbackFactory(CallbackData, prefix="exit_menu"):  # type: ignore
    pass


class SkipMenuCallbackFactory(CallbackData, prefix="skip_menu"):  # type: ignore
    pass


class ConfirmMenuCallbackFactory(CallbackData, prefix="confirm_menu"):  # type: ignore
    pass


class ToggleCallbackFactory(CallbackData, prefix="toggle_menu"):  # type: ignore
    is_on: bool


class NoopCallbackFactory(CallbackData, prefix="noop_menu"):  # type: ignore
    pass
