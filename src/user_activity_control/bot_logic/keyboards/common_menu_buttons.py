from copy import deepcopy

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dynaconf import Dynaconf

from user_activity_control.bot_logic.callback_classes.category_callbacks import CategoryCallbackFactory
from user_activity_control.bot_logic.callback_classes.common_menu_callbacks import (
    AdminMenuCallbackFactory,
    ConfirmMenuCallbackFactory,
    ExitMenuCallbackFactory,
    NoopCallbackFactory,
    SkipMenuCallbackFactory,
)
from user_activity_control.bot_logic.callback_classes.user_callbacks import UserCallbackFactory
from user_activity_control.infra.locale.types import LocaleFactory
from user_activity_control.infra.logger.types import LoggerFactory


class CommonMenuButtons:
    def __init__(self, logger_factory: LoggerFactory, settings: Dynaconf, locale_factory: LocaleFactory):
        self.logger = logger_factory(__name__)
        self.page_limit = settings.PAGINATION_LIMIT
        self._ = locale_factory

    def get_pagination_buttons(
        self,
        builder: InlineKeyboardBuilder,
        callback_data: CategoryCallbackFactory | UserCallbackFactory,
    ) -> InlineKeyboardBuilder:
        if callback_data.total <= self.page_limit:
            return builder

        callback_data.by_paginate_button = True

        if callback_data.page == 0:
            prev_button = InlineKeyboardButton(text=" ", callback_data=NoopCallbackFactory().pack())
        else:
            prev_callback_data = deepcopy(callback_data)
            prev_callback_data.page = prev_callback_data.page - 1
            prev_button = InlineKeyboardButton(
                text=self._("keyboard_back_button"),
                callback_data=prev_callback_data.pack(),
            )

        if (callback_data.page + 1) * self.page_limit > callback_data.total:
            next_button = InlineKeyboardButton(text=" ", callback_data=NoopCallbackFactory().pack())
        else:
            next_callback_data = deepcopy(callback_data)
            next_callback_data.page = next_callback_data.page + 1
            next_button = InlineKeyboardButton(
                text=self._("keyboard_forward_button"),
                callback_data=next_callback_data.pack(),
            )

        builder.row(prev_button, next_button)

        return builder

    def get_exit_button(self, builder: InlineKeyboardBuilder) -> InlineKeyboardBuilder:
        builder.row(
            InlineKeyboardButton(
                text=self._("keyboard_exit_button"),
                callback_data=ExitMenuCallbackFactory().pack(),
            )
        )
        return builder

    def get_skip_button(self, builder: InlineKeyboardBuilder) -> InlineKeyboardBuilder:
        builder.row(
            InlineKeyboardButton(
                text=self._("keyboard_skip_button"),
                callback_data=SkipMenuCallbackFactory().pack(),
            )
        )
        return builder

    def get_previous_button(self, builder: InlineKeyboardBuilder, callback_str: str) -> InlineKeyboardBuilder:
        builder.row(
            InlineKeyboardButton(
                text=self._("keyboard_previous_menu_button"),
                callback_data=callback_str,
            )
        )
        return builder

    def get_admin_menu_button(self, builder: InlineKeyboardBuilder) -> InlineKeyboardBuilder:
        builder.row(
            InlineKeyboardButton(text=self._("keyboard_start_button"), callback_data=AdminMenuCallbackFactory().pack())
        )
        return builder

    def get_confirm_remove_button(self, builder: InlineKeyboardBuilder) -> InlineKeyboardBuilder:
        builder.row(
            InlineKeyboardButton(
                text=self._("keyboard_remove_confirm_button"),
                callback_data=ConfirmMenuCallbackFactory().pack(),
            )
        )
        return builder
