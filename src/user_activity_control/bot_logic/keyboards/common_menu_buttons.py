from copy import deepcopy

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from user_activity_control.bot_logic.callback_classes.common_menu_callbacks import (
    AdminMenuCallbackFactory,
    ConfirmMenuCallbackFactory,
    ExitMenuCallbackFactory,
    NavigatorCallbackFactory,
    NoopCallbackFactory,
    SkipMenuCallbackFactory,
)
from user_activity_control.core.config import get_logger, get_settings
from user_activity_control.infra.locale.locale_utils import get_translate_string

logger = get_logger(__name__)


class CommonMenuButtons:
    page_limit = get_settings().PAGINATION_LIMIT
    _ = get_translate_string

    @classmethod
    def get_pagination_buttons(
        cls,
        builder: InlineKeyboardBuilder,
        callback_data: NavigatorCallbackFactory,
    ) -> InlineKeyboardBuilder:
        if callback_data.total <= cls.page_limit:
            return builder

        if callback_data.page == 0:
            prev_button = InlineKeyboardButton(text=" ", callback_data=NoopCallbackFactory().pack())
        else:
            prev_callback_data = deepcopy(callback_data)
            prev_callback_data.page = prev_callback_data.page - 1
            prev_button = InlineKeyboardButton(
                text=cls._("keyboard_back_button"),
                callback_data=prev_callback_data.pack(),
            )

        if (callback_data.page + 1) * cls.page_limit > callback_data.total:
            next_button = InlineKeyboardButton(text=" ", callback_data=NoopCallbackFactory().pack())
        else:
            next_callback_data = deepcopy(callback_data)
            next_callback_data.page = next_callback_data.page + 1
            next_button = InlineKeyboardButton(
                text=cls._("keyboard_forward_button"),
                callback_data=next_callback_data.pack(),
            )

        builder.row(prev_button, next_button)

        return builder

    @classmethod
    def get_exit_button(cls, builder: InlineKeyboardBuilder) -> InlineKeyboardBuilder:
        builder.row(
            InlineKeyboardButton(
                text=cls._("keyboard_exit_button"),
                callback_data=ExitMenuCallbackFactory().pack(),
            )
        )
        return builder

    @classmethod
    def get_skip_button(cls, builder: InlineKeyboardBuilder) -> InlineKeyboardBuilder:
        builder.row(
            InlineKeyboardButton(
                text=cls._("keyboard_skip_button"),
                callback_data=SkipMenuCallbackFactory().pack(),
            )
        )
        return builder

    @classmethod
    def get_previous_button(cls, builder: InlineKeyboardBuilder, callback_str: str) -> InlineKeyboardBuilder:
        builder.row(
            InlineKeyboardButton(
                text=cls._("keyboard_previous_menu_button"),
                callback_data=callback_str,
            )
        )
        return builder

    @classmethod
    def get_admin_menu_button(cls, builder: InlineKeyboardBuilder) -> InlineKeyboardBuilder:
        builder.row(
            InlineKeyboardButton(text=cls._("keyboard_start_button"), callback_data=AdminMenuCallbackFactory().pack())
        )
        return builder

    @classmethod
    def get_confirm_remove_button(cls, builder: InlineKeyboardBuilder) -> InlineKeyboardBuilder:
        builder.row(
            InlineKeyboardButton(
                text=cls._("keyboard_remove_confirm_button"),
                callback_data=ConfirmMenuCallbackFactory().pack(),
            )
        )
        return builder
