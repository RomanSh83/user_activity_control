from typing import Any

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dynaconf import Dynaconf

from user_activity_control.bot_logic.callback_classes.category_callbacks import CategoryCallbackFactory
from user_activity_control.bot_logic.callback_classes.common_menu_callbacks import (
    AdminMenuCallbackFactory,
    ConfirmMenuCallbackFactory,
    NavigatorCallbackFactory,
    SkipMenuCallbackFactory,
)
from user_activity_control.bot_logic.callback_classes.user_callbacks import UserCallbackFactory, UserUniqueReactions
from user_activity_control.bot_logic.enums.entity_enums import UserSettingsEnum
from user_activity_control.bot_logic.enums.menu_enums import MenuActionEnum, NavigatorEntityEnum
from user_activity_control.bot_logic.filters.permission_filters import AdminFilter
from user_activity_control.bot_logic.keyboards.keyboard_generator import KeyboardGenerator
from user_activity_control.bot_logic.schemas.user_schemas import UserSchema, UserUpdateSchema
from user_activity_control.bot_logic.services.admin_services.categories_services import CategoryService
from user_activity_control.bot_logic.services.admin_services.users_services import UserService
from user_activity_control.bot_logic.services.bot_services.send_message_service import MessageService
from user_activity_control.bot_logic.services.bot_services.state_services import StateService
from user_activity_control.bot_logic.states.user_states import CreateUserStates, RemoveUserStates, UpdateUserStates
from user_activity_control.bot_logic.validators.user_validators import UserValidator
from user_activity_control.core.config import get_logger
from user_activity_control.infra.locale.types import Locale

admin_user_router = Router()
admin_user_router.callback_query.filter(AdminFilter())


logger = get_logger(__name__)


@admin_user_router.callback_query(UserCallbackFactory.filter(F.action == MenuActionEnum.LIST))
async def list_users_handler(
    callback: CallbackQuery,
    state: FSMContext,
    settings: Dynaconf,
    user_settings: dict[str, dict[str, Any]],
    keyboard_generator: KeyboardGenerator,
    user_service: UserService,
    message_service: MessageService,
    _: Locale,
) -> None:
    await callback.answer()

    limit = settings.PAGINATION_LIMIT
    users_total = len(user_settings)
    callback_data = NavigatorCallbackFactory(page=0, total=users_total, entity=NavigatorEntityEnum.USERS)
    current_users = user_service.get_users(offset=callback_data.page * limit, limit=limit)
    back_callback_str = AdminMenuCallbackFactory().pack()
    text = _("admin_users_list") if users_total != 0 else _("admin_users_list_empty")

    await message_service.send_message(
        event=callback,
        state=state,
        text=text,
        reply_markup=keyboard_generator.get_user_list_keyboard(
            users=current_users, callback_data=callback_data, back_callback_str=back_callback_str
        ),
    )


@admin_user_router.callback_query(UserCallbackFactory.filter(F.action == MenuActionEnum.RETRIEVE))
async def retrieve_user_handler(
    callback: CallbackQuery,
    callback_data: UserCallbackFactory,
    keyboard_generator: KeyboardGenerator,
    category_service: CategoryService,
    user_service: UserService,
    state: FSMContext,
    message_service: MessageService,
    _: Locale,
) -> None:
    await callback.answer()

    if callback_data.uid is None:
        return

    user = user_service.get_user(user_id=callback_data.uid)
    category = category_service.get_category(category_slug=user.category)

    await state.update_data(user=user.model_dump())

    back_callback_str = UserCallbackFactory(action=MenuActionEnum.LIST).pack()

    await message_service.send_message(
        event=callback,
        state=state,
        text=_(
            "admin_user_retrieve",
            user_id=user.user_id,
            category_name=category.name,
            chat_ids=", ".join(user.chat_ids),
            inactivity_alert_delay=user.inactivity_alert_delay,
            stand_down_delay=user.stand_down_delay,
            unique_command_reactions=user.unique_command_reactions,
        ),
        reply_markup=keyboard_generator.get_user_retrieve_keyboard(user=user, back_callback_str=back_callback_str),
    )


@admin_user_router.callback_query(UserCallbackFactory.filter(F.action == MenuActionEnum.CREATE))
async def create_user_id_request_handler(
    callback: CallbackQuery,
    keyboard_generator: KeyboardGenerator,
    state: FSMContext,
    message_service: MessageService,
    _: Locale,
) -> None:
    await callback.answer()

    await state.set_state(CreateUserStates.wait_id)
    await message_service.send_message(
        event=callback,
        state=state,
        text=_("admin_user_create_id"),
        reply_markup=keyboard_generator.get_add_edit_keyboard(back_callback_str=AdminMenuCallbackFactory().pack()),
    )


@admin_user_router.message(StateFilter(CreateUserStates.wait_id))
@admin_user_router.callback_query(UserCallbackFactory.filter(F.action == MenuActionEnum.UPDATE))
async def create_update_user_category_request_handler(
    event: Message | CallbackQuery,
    keyboard_generator: KeyboardGenerator,
    state: FSMContext,
    settings: Dynaconf,
    categories: dict[str, dict[str, Any]],
    category_service: CategoryService,
    message_service: MessageService,
    user_validator: UserValidator,
    _: Locale,
) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()

    user_data = {}
    if isinstance(event, Message):
        user_id, validate_error_text = await user_validator.validate_id(value=event.text)
        if validate_error_text:
            kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=AdminMenuCallbackFactory().pack())
            await message_service.send_message(event=event, state=state, text=validate_error_text, reply_markup=kb)
            return
        user_data = {UserSettingsEnum.USER_ID: user_id}

    if not len(categories):
        await message_service.send_message(
            event=event,
            state=state,
            text=_("admin_user_create_not_categories"),
            reply_markup=keyboard_generator.get_complete_action_keyboard(),
        )
        return

    limit = settings.PAGINATION_LIMIT
    categories_total = len(categories)
    callback_data = NavigatorCallbackFactory(
        page=0, total=categories_total, entity=NavigatorEntityEnum.CATEGORIES, from_action=MenuActionEnum.CHOICE
    )
    current_categories = category_service.get_categories(offset=callback_data.page * limit, limit=limit)

    if await state.get_state() == CreateUserStates.wait_id:
        text = _("admin_user_create_category")
        kb = keyboard_generator.get_category_list_keyboard(
            categories=current_categories,
            callback_data=callback_data,
            back_callback_str=AdminMenuCallbackFactory().pack(),
        )
        new_state = CreateUserStates.wait_category
    else:
        fsm_data = await state.get_data()
        user = UserSchema(**fsm_data["user"])
        category = category_service.get_category(category_slug=user.category)
        text = _("admin_user_update_category", category_name=category.name)
        kb = keyboard_generator.get_category_list_keyboard(
            categories=current_categories,
            callback_data=callback_data,
            back_callback_str=UserCallbackFactory(action=MenuActionEnum.RETRIEVE, uid=user.user_id).pack(),
            skip_button=True,
        )
        new_state = UpdateUserStates.wait_category

    await state.update_data(user_data=user_data)
    await state.set_state(new_state)

    await message_service.send_message(event=event, state=state, text=text, reply_markup=kb)


@admin_user_router.callback_query(
    CategoryCallbackFactory.filter(F.action == MenuActionEnum.CHOICE),
    StateFilter(CreateUserStates.wait_category, UpdateUserStates.wait_category),
)
@admin_user_router.callback_query(SkipMenuCallbackFactory.filter(), StateFilter(UpdateUserStates.wait_category))
async def create_update_user_category_handler(
    callback: CallbackQuery,
    callback_data: CategoryCallbackFactory | SkipMenuCallbackFactory,
    keyboard_generator: KeyboardGenerator,
    state: FSMContext,
    message_service: MessageService,
    _: Locale,
) -> None:
    await callback.answer()

    fsm_data = await state.get_data()
    user_data = fsm_data["user_data"]

    if isinstance(callback_data, CategoryCallbackFactory):
        user_data[UserSettingsEnum.CATEGORY] = callback_data.slug

    if await state.get_state() == CreateUserStates.wait_category:
        text = _("admin_user_create_chat_ids")
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=AdminMenuCallbackFactory().pack())
        new_state = CreateUserStates.wait_chat_ids

    else:
        user = UserSchema(**fsm_data["user"])
        text = _("admin_user_update_chat_ids", chat_ids="\n".join(user.chat_ids))
        kb = keyboard_generator.get_add_edit_keyboard(
            back_callback_str=AdminMenuCallbackFactory().pack(), skip_button=True
        )
        new_state = UpdateUserStates.wait_chat_ids

    await state.update_data(user_data=user_data)
    await state.set_state(new_state)

    await message_service.send_message(event=callback, state=state, text=text, reply_markup=kb)


@admin_user_router.message(StateFilter(CreateUserStates.wait_chat_ids, UpdateUserStates.wait_chat_ids))
@admin_user_router.callback_query(SkipMenuCallbackFactory.filter(), StateFilter(UpdateUserStates.wait_chat_ids))
async def create_update_user_chat_ids_handler(
    event: Message | CallbackQuery,
    keyboard_generator: KeyboardGenerator,
    state: FSMContext,
    user_validator: UserValidator,
    message_service: MessageService,
    _: Locale,
) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()

    fsm_data = await state.get_data()
    user_data = fsm_data["user_data"]

    if await state.get_state() == CreateUserStates.wait_chat_ids:
        text = _("admin_user_create_inactivity_alert_delay")
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=AdminMenuCallbackFactory().pack())
        new_state = CreateUserStates.wait_inactivity_alert_delay

    else:
        user = UserSchema(**fsm_data["user"])
        text = _("admin_user_update_inactivity_alert_delay", alert_delay=user.inactivity_alert_delay)
        kb = keyboard_generator.get_add_edit_keyboard(
            back_callback_str=AdminMenuCallbackFactory().pack(), skip_button=True
        )
        new_state = UpdateUserStates.wait_inactivity_alert_delay

    if isinstance(event, Message):
        chat_ids, validate_error_text = await user_validator.validate_chat_ids(value=event.text)
        if validate_error_text:
            await message_service.send_message(event=event, state=state, text=validate_error_text, reply_markup=kb)
            return
        user_data[UserSettingsEnum.CHAT_IDS] = chat_ids

    await state.update_data(user_data=user_data)
    await state.set_state(new_state)

    await message_service.send_message(event=event, state=state, text=text, reply_markup=kb)


@admin_user_router.message(
    StateFilter(CreateUserStates.wait_inactivity_alert_delay, UpdateUserStates.wait_inactivity_alert_delay)
)
@admin_user_router.callback_query(
    SkipMenuCallbackFactory.filter(), StateFilter(UpdateUserStates.wait_inactivity_alert_delay)
)
async def create_update_user_inactivity_alert_delay_handler(
    event: Message | CallbackQuery,
    keyboard_generator: KeyboardGenerator,
    state: FSMContext,
    user_validator: UserValidator,
    message_service: MessageService,
    _: Locale,
) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()

    fsm_data = await state.get_data()
    user_data = fsm_data["user_data"]

    if await state.get_state() == CreateUserStates.wait_inactivity_alert_delay:
        text = _("admin_user_create_stand_down_delay")
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=AdminMenuCallbackFactory().pack())
        new_state = CreateUserStates.wait_stand_down_delay

    else:
        user = UserSchema(**fsm_data["user"])
        text = _("admin_user_update_stand_down_delay", stand_down_delay=user.stand_down_delay)
        kb = keyboard_generator.get_add_edit_keyboard(
            back_callback_str=AdminMenuCallbackFactory().pack(), skip_button=True
        )
        new_state = UpdateUserStates.wait_stand_down_delay

    if isinstance(event, Message):
        inactivity_alert_delay, validate_error_text = await user_validator.validate_inactivity_alert_delay(
            value=event.text
        )
        if validate_error_text:
            await message_service.send_message(event=event, state=state, text=validate_error_text, reply_markup=kb)
            return
        user_data[UserSettingsEnum.INACTIVITY_ALERT_DELAY] = inactivity_alert_delay

    await state.update_data(user_data=user_data)
    await state.set_state(new_state)

    await message_service.send_message(event=event, state=state, text=text, reply_markup=kb)


@admin_user_router.message(StateFilter(CreateUserStates.wait_stand_down_delay, UpdateUserStates.wait_stand_down_delay))
@admin_user_router.callback_query(SkipMenuCallbackFactory.filter(), StateFilter(UpdateUserStates.wait_stand_down_delay))
async def create_update_user_stand_down_delay_handler(
    event: Message | CallbackQuery,
    keyboard_generator: KeyboardGenerator,
    state: FSMContext,
    user_validator: UserValidator,
    message_service: MessageService,
    _: Locale,
) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()

    fsm_data = await state.get_data()
    user_data = fsm_data["user_data"]

    if await state.get_state() == CreateUserStates.wait_stand_down_delay:
        text = _("admin_user_create_unique_command_reactions")
        skip_button = False
        kb = keyboard_generator.get_user_unique_reactions_keyboard(back_callback_str=AdminMenuCallbackFactory().pack())
        new_state = CreateUserStates.wait_unique_command_reactions

    else:
        user = UserSchema(**fsm_data["user"])
        text = _("admin_user_update_unique_command_reactions", unique_command_reactions=user.unique_command_reactions)
        skip_button = True
        kb = keyboard_generator.get_user_unique_reactions_keyboard(
            back_callback_str=AdminMenuCallbackFactory().pack(),
            on_button=not user.unique_command_reactions,
            off_button=user.unique_command_reactions,
            skip_button=skip_button,
        )
        new_state = UpdateUserStates.wait_unique_command_reactions

    if isinstance(event, Message):
        stand_down_delay, validate_error_text = await user_validator.validate_stand_down_delay(value=event.text)
        if validate_error_text:
            await message_service.send_message(
                event=event,
                state=state,
                text=validate_error_text,
                reply_markup=keyboard_generator.get_add_edit_keyboard(
                    back_callback_str=AdminMenuCallbackFactory().pack(), skip_button=skip_button
                ),
            )
            return
        user_data[UserSettingsEnum.STAND_DOWN_DELAY] = stand_down_delay

    await state.update_data(user_data=user_data)
    await state.set_state(new_state)

    await message_service.send_message(event=event, state=state, text=text, reply_markup=kb)


@admin_user_router.callback_query(
    UserUniqueReactions.filter(),
    StateFilter(CreateUserStates.wait_unique_command_reactions, UpdateUserStates.wait_unique_command_reactions),
)
@admin_user_router.callback_query(
    SkipMenuCallbackFactory.filter(), StateFilter(UpdateUserStates.wait_unique_command_reactions)
)
async def create_update_user_unique_command_reactions_handler(
    callback: CallbackQuery,
    callback_data: UserUniqueReactions,
    keyboard_generator: KeyboardGenerator,
    state: FSMContext,
    user_service: UserService,
    message_service: MessageService,
    state_service: StateService,
    _: Locale,
) -> None:
    await callback.answer()

    fsm_data = await state.get_data()
    user_data = fsm_data["user_data"]

    if isinstance(callback_data, UserUniqueReactions):
        user_data[UserSettingsEnum.UNIQUE_COMMAND_REACTION] = callback_data.is_enabled

    if await state.get_state() == CreateUserStates.wait_unique_command_reactions:
        text = _("admin_user_created_successfully", user_id=user_data[UserSettingsEnum.USER_ID])
        user_service.create_user(user=UserSchema(**user_data))
    else:
        user = UserSchema(**fsm_data["user"])
        text = _("admin_user_updated_successfully", user_id=user.user_id)
        user_service.update_user(user_id=user.user_id, user_data=UserUpdateSchema(**user_data))

    await state_service.safe_clear(state=state)

    await message_service.send_message(
        event=callback, state=state, text=text, reply_markup=keyboard_generator.get_complete_action_keyboard()
    )


@admin_user_router.callback_query(UserCallbackFactory.filter(F.action == MenuActionEnum.REMOVE))
async def remove_user_request_handler(
    callback: CallbackQuery, state: FSMContext, keyboard_generator: KeyboardGenerator, _: Locale
) -> None:
    await callback.answer()

    fsm_data = await state.get_data()
    user = UserSchema(**fsm_data["user"])
    back_callback_str = UserCallbackFactory(action=MenuActionEnum.RETRIEVE, uid=user.user_id).pack()

    text = _("admin_user_remove_request", user_id=user.user_id)

    kb = keyboard_generator.get_confirmation_keyboard(back_callback_str=back_callback_str)

    await state.set_state(RemoveUserStates.wait_confirmation)
    await callback.message.answer(text=text, reply_markup=kb)


@admin_user_router.callback_query(ConfirmMenuCallbackFactory.filter(), StateFilter(RemoveUserStates.wait_confirmation))
async def remove_category_handler(
    callback: CallbackQuery,
    state: FSMContext,
    user_service: UserService,
    keyboard_generator: KeyboardGenerator,
    _: Locale,
) -> None:
    await callback.answer()

    fsm_data = await state.get_data()
    user = UserSchema(**fsm_data["user"])

    user_service.remove_user(user_id=user.user_id)

    await callback.message.answer(
        text=_("admin_user_successfully_removed", user_id=user.user_id),
        reply_markup=keyboard_generator.get_complete_action_keyboard(),
    )
