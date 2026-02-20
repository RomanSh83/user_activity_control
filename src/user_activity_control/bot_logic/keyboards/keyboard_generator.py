from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from user_activity_control.bot_logic.callback_classes.category_callbacks import CategoryCallbackFactory
from user_activity_control.bot_logic.callback_classes.user_callbacks import UserCallbackFactory, UserUniqueReactions
from user_activity_control.bot_logic.enums.menu_enums import MenuActionEnum
from user_activity_control.bot_logic.keyboards.common_menu_buttons import CommonMenuButtons
from user_activity_control.bot_logic.schemas.category_schemas import CategorySchema
from user_activity_control.bot_logic.schemas.user_schemas import UserSchema
from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_logger
from user_activity_control.infra.locale.locale_utils import get_translate_string

logger = get_logger(__name__)


class MenuButtons:
    pass


class KeyboardGenerator(Singleton):
    def __init__(self):
        self._ = get_translate_string
        self.common_buttons = CommonMenuButtons

    def get_admin_keyboard(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=self._("keyboard_list_categories_button"),
            callback_data=CategoryCallbackFactory(action=MenuActionEnum.LIST).pack(),
        )
        builder.button(
            text=self._("keyboard_list_users_button"),
            callback_data=UserCallbackFactory(action=MenuActionEnum.LIST).pack(),
        )
        builder.adjust(1)

        self.common_buttons.get_exit_button(builder=builder)

        return builder.as_markup()

    def get_category_list_keyboard(
        self,
        categories: list[CategorySchema],
        callback_data: CategoryCallbackFactory,
        skip_button: bool = False,
        back_callback_str: str | None = None,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        action = (
            callback_data.action.CHOICE
            if callback_data.action == MenuActionEnum.CHOICE_LIST
            else MenuActionEnum.RETRIEVE
        )
        for category in categories:
            builder.button(
                text=category.name.capitalize(),
                callback_data=CategoryCallbackFactory(action=action, category_id=category.category_id),
            )
        builder.adjust(1)

        self.common_buttons.get_pagination_buttons(builder=builder, callback_data=callback_data)

        if callback_data.action == MenuActionEnum.LIST:
            builder.row(
                InlineKeyboardButton(
                    text=self._("keyboard_create_category_button"),
                    callback_data=CategoryCallbackFactory(action=MenuActionEnum.CREATE).pack(),
                )
            )

        if skip_button:
            self.common_buttons.get_skip_button(builder=builder)

        if back_callback_str:
            self.common_buttons.get_previous_button(builder=builder, callback_str=back_callback_str)

        self.common_buttons.get_exit_button(builder=builder)

        return builder.as_markup()

    def get_category_retrieve_keyboard(self, category: CategorySchema, back_callback_str: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text=self._("keyboard_update_category_button"),
                callback_data=CategoryCallbackFactory(
                    action=MenuActionEnum.UPDATE, category_id=category.category_id
                ).pack(),
            )
        )
        builder.row(
            InlineKeyboardButton(
                text=self._("keyboard_remove_category_button"),
                callback_data=CategoryCallbackFactory(
                    action=MenuActionEnum.REMOVE, category_id=category.category_id
                ).pack(),
            )
        )

        self.common_buttons.get_previous_button(builder=builder, callback_str=back_callback_str)

        self.common_buttons.get_exit_button(builder=builder)

        return builder.as_markup()

    def get_add_edit_keyboard(
        self, back_callback_str: str | None = None, skip_button: bool = False
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if skip_button:
            self.common_buttons.get_skip_button(builder=builder)

        if back_callback_str:
            self.common_buttons.get_previous_button(builder=builder, callback_str=back_callback_str)

        self.common_buttons.get_exit_button(builder=builder)

        return builder.as_markup()

    def get_complete_action_keyboard(self, back_callback_str: str | None = None) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if back_callback_str:
            self.common_buttons.get_previous_button(builder=builder, callback_str=back_callback_str)

        self.common_buttons.get_admin_menu_button(builder=builder)

        self.common_buttons.get_exit_button(builder=builder)

        return builder.as_markup()

    def get_confirmation_keyboard(self, back_callback_str: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        self.common_buttons.get_confirm_remove_button(builder=builder)

        self.common_buttons.get_previous_button(builder=builder, callback_str=back_callback_str)

        self.common_buttons.get_exit_button(builder=builder)

        return builder.as_markup()

    def get_user_list_keyboard(
        self,
        users: list[UserSchema],
        callback_data: UserCallbackFactory,
        back_callback_str: str | None = None,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        action = MenuActionEnum.RETRIEVE
        for user in users:
            builder.button(
                text=user.user_id,
                callback_data=UserCallbackFactory(action=action, uid=user.user_id),
            )
        builder.adjust(1)

        self.common_buttons.get_pagination_buttons(builder=builder, callback_data=callback_data)

        builder.row(
            InlineKeyboardButton(
                text=self._("keyboard_create_user_button"),
                callback_data=UserCallbackFactory(action=MenuActionEnum.CREATE).pack(),
            )
        )

        if back_callback_str:
            self.common_buttons.get_previous_button(builder=builder, callback_str=back_callback_str)

        self.common_buttons.get_exit_button(builder=builder)

        return builder.as_markup()

    def get_user_retrieve_keyboard(self, user: UserSchema, back_callback_str: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text=self._("keyboard_update_user_button"),
                callback_data=UserCallbackFactory(action=MenuActionEnum.UPDATE, uid=user.user_id).pack(),
            )
        )
        builder.row(
            InlineKeyboardButton(
                text=self._("keyboard_remove_user_button"),
                callback_data=UserCallbackFactory(action=MenuActionEnum.REMOVE, uid=user.user_id).pack(),
            )
        )

        self.common_buttons.get_previous_button(builder=builder, callback_str=back_callback_str)

        self.common_buttons.get_exit_button(builder=builder)

        return builder.as_markup()

    def get_user_unique_reactions_keyboard(
        self,
        on_button: bool = True,
        off_button: bool = True,
        back_callback_str: str | None = None,
        skip_button: bool = False,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if on_button:
            builder.row(
                InlineKeyboardButton(
                    text=self._("keyboard_unique_reactions_on_button"),
                    callback_data=UserUniqueReactions().pack(),
                )
            )

        if off_button:
            builder.row(
                InlineKeyboardButton(
                    text=self._("keyboard_unique_reactions_off_button"),
                    callback_data=UserUniqueReactions(is_enabled=False).pack(),
                )
            )

        if skip_button:
            self.common_buttons.get_skip_button(builder=builder)

        if back_callback_str:
            self.common_buttons.get_previous_button(builder=builder, callback_str=back_callback_str)

        self.common_buttons.get_exit_button(builder=builder)

        return builder.as_markup()
