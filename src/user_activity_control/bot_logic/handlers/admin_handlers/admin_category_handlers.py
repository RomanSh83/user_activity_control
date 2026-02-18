from pathlib import Path
from typing import Any

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from dynaconf import Dynaconf

from user_activity_control.bot_logic.callback_classes.category_callbacks import CategoryCallbackFactory
from user_activity_control.bot_logic.callback_classes.common_menu_callbacks import (
    AdminMenuCallbackFactory,
    ConfirmMenuCallbackFactory,
    NavigatorCallbackFactory,
    SkipMenuCallbackFactory,
)
from user_activity_control.bot_logic.enums.menu_enums import MenuActionEnum, NavigatorEntityEnum
from user_activity_control.bot_logic.filters.permission_filters import AdminFilter
from user_activity_control.bot_logic.keyboards.keyboard_generator import KeyboardGenerator
from user_activity_control.bot_logic.schemas.category_schemas import CategorySchema
from user_activity_control.bot_logic.services.admin_services.categories_services import CategoryService
from user_activity_control.bot_logic.services.admin_services.users_services import UserService
from user_activity_control.bot_logic.services.bot_services.send_message_service import MessageService
from user_activity_control.bot_logic.services.bot_services.state_services import StateService
from user_activity_control.bot_logic.states.category_states import (
    CreateCategoryStates,
    RemoveCategoryStates,
    UpdateCategoryStates,
)
from user_activity_control.bot_logic.validators.category_validators import CategoryValidator
from user_activity_control.core.config import get_logger
from user_activity_control.infra.locale.types import Locale

admin_category_router = Router()
admin_category_router.callback_query.filter(AdminFilter())


logger = get_logger(__name__)


@admin_category_router.callback_query(CategoryCallbackFactory.filter(F.action == MenuActionEnum.LIST))
async def list_categories_handler(
    callback: CallbackQuery,
    state: FSMContext,
    settings: Dynaconf,
    categories: dict[str, dict[str, Any]],
    keyboard_generator: KeyboardGenerator,
    category_service: CategoryService,
    message_service: MessageService,
    _: Locale,
) -> None:
    await callback.answer()

    limit = settings.PAGINATION_LIMIT
    categories_total = len(categories)
    callback_data = NavigatorCallbackFactory(page=0, total=categories_total, entity=NavigatorEntityEnum.CATEGORIES)
    current_categories = category_service.get_categories(offset=callback_data.page * limit, limit=limit)
    back_callback_str = AdminMenuCallbackFactory().pack()
    text = _("admin_category_list") if categories_total != 0 else _("admin_category_list_empty")

    await message_service.send_message(
        event=callback,
        state=state,
        text=text,
        reply_markup=keyboard_generator.get_category_list_keyboard(
            categories=current_categories, callback_data=callback_data, back_callback_str=back_callback_str
        ),
    )


@admin_category_router.callback_query(CategoryCallbackFactory.filter(F.action == MenuActionEnum.RETRIEVE))
async def retrieve_category_handler(
    callback: CallbackQuery,
    callback_data: CategoryCallbackFactory,
    keyboard_generator: KeyboardGenerator,
    category_service: CategoryService,
    state: FSMContext,
    message_service: MessageService,
    _: Locale,
) -> None:
    await callback.answer()

    if callback_data.slug is None:
        return

    category = category_service.get_category(category_slug=callback_data.slug)

    await state.update_data(category=category.model_dump())

    back_callback_str = CategoryCallbackFactory(action=MenuActionEnum.LIST).pack()

    await message_service.send_message(
        event=callback,
        state=state,
        text=_("admin_category_retrieve", category=category.name),
        reply_markup=keyboard_generator.get_category_retrieve_keyboard(
            category=category, back_callback_str=back_callback_str
        ),
    )


@admin_category_router.callback_query(
    CategoryCallbackFactory.filter(F.action.in_((MenuActionEnum.CREATE, MenuActionEnum.UPDATE)))
)
async def create_update_category_handler(
    callback: CallbackQuery,
    callback_data: CategoryCallbackFactory,
    keyboard_generator: KeyboardGenerator,
    state: FSMContext,
    settings: Dynaconf,
    message_service: MessageService,
    _: Locale,
) -> None:
    await callback.answer()

    if callback_data.action == MenuActionEnum.CREATE:
        text = _("admin_category_create_name", max_length=settings.MAX_CATEGORY_NAME_LENGTH)
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=AdminMenuCallbackFactory().pack())
        new_state = CreateCategoryStates.wait_name
    else:
        fsm_data = await state.get_data()
        category = CategorySchema(**fsm_data["category"])
        text = _("admin_category_update_name", name=category.name, max_length=settings.MAX_CATEGORY_NAME_LENGTH)
        kb = keyboard_generator.get_add_edit_keyboard(
            back_callback_str=CategoryCallbackFactory(action=MenuActionEnum.RETRIEVE, slug=callback_data.slug).pack(),
            skip_button=True,
        )
        new_state = UpdateCategoryStates.wait_name

    await state.set_state(new_state)
    await message_service.send_message(event=callback, state=state, text=text, reply_markup=kb)


@admin_category_router.message(StateFilter(CreateCategoryStates.wait_name, UpdateCategoryStates.wait_name))
@admin_category_router.callback_query(SkipMenuCallbackFactory.filter(), StateFilter(UpdateCategoryStates.wait_name))
async def create_update_category_name_handler(
    event: Message | CallbackQuery,
    state: FSMContext,
    category_validator: CategoryValidator,
    keyboard_generator: KeyboardGenerator,
    message_service: MessageService,
    base_dir: Path,
    _: Locale,
    callback: CallbackQuery | None = None,
) -> None:
    if callback:
        await callback.answer()

    document = FSInputFile(base_dir / "app_data" / "examples" / "templates_example.yaml")

    if await state.get_state() == CreateCategoryStates.wait_name:
        slug = None
        name = None
        back_callback_str = AdminMenuCallbackFactory().pack()
        text = _("admin_category_create_template_file")
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str)
        new_state = CreateCategoryStates.wait_template_file

    else:
        fsm_data = await state.get_data()
        current_category = CategorySchema(**fsm_data["category"])
        slug = current_category.slug
        name = current_category.name
        back_callback_str = CategoryCallbackFactory(action=MenuActionEnum.RETRIEVE, slug=current_category.slug).pack()
        file_path = base_dir / "app_data" / "strings" / current_category.slug / "templates.yaml"
        if Path.exists(file_path):
            document = FSInputFile(file_path)
            text = _("admin_category_update_template_file_exists")
            kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)
            new_state = UpdateCategoryStates.wait_optional_template_file
        else:
            text = _("admin_category_update_template_file_not_exists")
            kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str)
            new_state = UpdateCategoryStates.wait_required_template_file

    if isinstance(event, Message):
        slug, name, validate_error_text = await category_validator.validate_name(name=event.text)
        if validate_error_text:
            await message_service.send_message(event=event, state=state, text=validate_error_text, reply_markup=kb)
            return

    await state.update_data(category_data={"name": name, "slug": slug})
    await state.set_state(new_state)
    await message_service.send_message(event=event, state=state, document=document, text=text, reply_markup=kb)


@admin_category_router.message(
    StateFilter(
        CreateCategoryStates.wait_template_file,
        UpdateCategoryStates.wait_optional_template_file,
        UpdateCategoryStates.wait_required_template_file,
    )
)
@admin_category_router.callback_query(
    SkipMenuCallbackFactory.filter(),
    StateFilter(
        CreateCategoryStates.wait_template_file,
        UpdateCategoryStates.wait_optional_template_file,
        UpdateCategoryStates.wait_required_template_file,
    ),
)
async def create_update_category_templates_file_handler(
    event: Message | CallbackQuery,
    state: FSMContext,
    category_validator: CategoryValidator,
    keyboard_generator: KeyboardGenerator,
    message_service: MessageService,
    base_dir: Path,
    _: Locale,
    callback: CallbackQuery | None = None,
) -> None:
    if callback:
        await callback.answer()

    fsm_data = await state.get_data()
    strings_data = {}
    document = FSInputFile(base_dir / "app_data" / "examples" / "alarm_example.yaml")

    if await state.get_state() == CreateCategoryStates.wait_template_file:
        back_callback_str = AdminMenuCallbackFactory().pack()
        text = _("admin_category_create_alarm_file")
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)
        new_state = CreateCategoryStates.wait_alarm_file

    else:
        current_category = CategorySchema(**fsm_data["category"])
        back_callback_str = CategoryCallbackFactory(action=MenuActionEnum.RETRIEVE, slug=current_category.slug).pack()
        file_path = base_dir / "app_data" / "strings" / current_category.slug / "alarm.yaml"
        if Path.exists(file_path):
            document = FSInputFile(file_path)
            text = _("admin_category_update_alarm_file_exists")
        else:
            text = _("admin_category_update_alarm_file_not_exists")
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)
        new_state = UpdateCategoryStates.wait_alarm_file

    if isinstance(event, Message):
        templates, validate_error_text = await category_validator.validate_templates_file(message=event)
        if validate_error_text:
            if await state.get_state() == UpdateCategoryStates.wait_required_template_file:
                kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str)
            await message_service.send_message(event=event, state=state, text=validate_error_text, reply_markup=kb)
            return
        strings_data["templates"] = templates

    await state.update_data(strings_data=strings_data)
    await state.set_state(new_state)
    await message_service.send_message(event=event, state=state, document=document, text=text, reply_markup=kb)


@admin_category_router.message(StateFilter(CreateCategoryStates.wait_alarm_file, UpdateCategoryStates.wait_alarm_file))
@admin_category_router.callback_query(
    SkipMenuCallbackFactory.filter(),
    StateFilter(CreateCategoryStates.wait_alarm_file, UpdateCategoryStates.wait_alarm_file),
)
async def create_update_category_alarm_file_handler(
    event: Message | CallbackQuery,
    state: FSMContext,
    category_validator: CategoryValidator,
    keyboard_generator: KeyboardGenerator,
    message_service: MessageService,
    base_dir: Path,
    _: Locale,
    callback: CallbackQuery | None = None,
) -> None:
    if callback:
        await callback.answer()

    fsm_data = await state.get_data()
    strings_data = fsm_data.get("strings_data")
    document = FSInputFile(base_dir / "app_data" / "examples" / "stand_down_example.yaml")

    if await state.get_state() == CreateCategoryStates.wait_alarm_file:
        back_callback_str = AdminMenuCallbackFactory().pack()
        text = _("admin_category_create_stand_down_file")
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)
        new_state = CreateCategoryStates.wait_stand_down_file

    else:
        current_category = CategorySchema(**fsm_data["category"])
        back_callback_str = CategoryCallbackFactory(action=MenuActionEnum.RETRIEVE, slug=current_category.slug).pack()
        file_path = base_dir / "app_data" / "strings" / current_category.slug / "stand_down.yaml"
        if Path.exists(file_path):
            document = FSInputFile(file_path)
            text = _("admin_category_update_stand_down_file_exists")
        else:
            text = _("admin_category_update_stand_down_file_not_exists")
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)
        new_state = UpdateCategoryStates.wait_stand_down_file

    if isinstance(event, Message):
        alarm, validate_error_text = await category_validator.validate_strings_file(message=event)
        if validate_error_text:
            await message_service.send_message(event=event, state=state, text=validate_error_text, reply_markup=kb)
            return
        strings_data["alarm"] = alarm

    await state.update_data(strings_data=strings_data)
    await state.set_state(new_state)
    await message_service.send_message(event=event, state=state, document=document, text=text, reply_markup=kb)


@admin_category_router.message(
    StateFilter(CreateCategoryStates.wait_stand_down_file, UpdateCategoryStates.wait_stand_down_file)
)
@admin_category_router.callback_query(
    SkipMenuCallbackFactory.filter(),
    StateFilter(CreateCategoryStates.wait_stand_down_file, UpdateCategoryStates.wait_stand_down_file),
)
async def create_update_category_stand_down_file_handler(
    event: Message | CallbackQuery,
    state: FSMContext,
    category_validator: CategoryValidator,
    keyboard_generator: KeyboardGenerator,
    message_service: MessageService,
    base_dir: Path,
    _: Locale,
    callback: CallbackQuery | None = None,
) -> None:
    if callback:
        await callback.answer()
    fsm_data = await state.get_data()
    strings_data = fsm_data.get("strings_data")
    document = FSInputFile(base_dir / "app_data" / "examples" / "command_example.yaml")

    if await state.get_state() == CreateCategoryStates.wait_stand_down_file:
        back_callback_str = AdminMenuCallbackFactory().pack()
        text = _("admin_category_create_command_file")
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)
        new_state = CreateCategoryStates.wait_command_file

    else:
        current_category = CategorySchema(**fsm_data["category"])
        back_callback_str = CategoryCallbackFactory(action=MenuActionEnum.RETRIEVE, slug=current_category.slug).pack()
        file_path = base_dir / "app_data" / "strings" / current_category.slug / "command.yaml"
        if Path.exists(file_path):
            document = FSInputFile(file_path)
            text = _("admin_category_update_command_file_exists")
        else:
            text = _("admin_category_update_command_file_not_exists")
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)
        new_state = UpdateCategoryStates.wait_command_file

    if isinstance(event, Message):
        stand_down, validate_error_text = await category_validator.validate_strings_file(message=event)
        if validate_error_text:
            await message_service.send_message(event=event, state=state, text=validate_error_text, reply_markup=kb)
            return
        strings_data["stand_down"] = stand_down

    await state.update_data(strings_data=strings_data)
    await state.set_state(new_state)
    await message_service.send_message(event=event, state=state, document=document, text=text, reply_markup=kb)


@admin_category_router.message(
    StateFilter(CreateCategoryStates.wait_command_file, UpdateCategoryStates.wait_command_file)
)
@admin_category_router.callback_query(
    SkipMenuCallbackFactory.filter(),
    StateFilter(CreateCategoryStates.wait_command_file, UpdateCategoryStates.wait_command_file),
)
async def create_update_category_command_file_handler(
    event: Message | CallbackQuery,
    state: FSMContext,
    category_validator: CategoryValidator,
    category_service: CategoryService,
    keyboard_generator: KeyboardGenerator,
    message_service: MessageService,
    state_service: StateService,
    _: Locale,
) -> None:
    fsm_data = await state.get_data()
    category_data = CategorySchema(**fsm_data["category_data"])
    strings_data = fsm_data.get("strings_data")

    if await state.get_state() == CreateCategoryStates.wait_command_file:
        back_callback_str = AdminMenuCallbackFactory().pack()
        text = _("admin_category_created_successfully", name=category_data.name)
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)
    else:
        current_category = CategorySchema(**fsm_data["category"])
        back_callback_str = CategoryCallbackFactory(action=MenuActionEnum.RETRIEVE, slug=current_category.slug).pack()
        text = _("admin_category_updated_successfully", name=category_data.name)
        kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)

    if isinstance(event, Message):
        command, validate_error_text = await category_validator.validate_strings_file(message=event)
        if validate_error_text:
            await message_service.send_message(event=event, state=state, text=validate_error_text, reply_markup=kb)
            return
        strings_data["command"] = command

    if await state.get_state() == CreateCategoryStates.wait_command_file:
        category_service.create_category(category_data=category_data, strings_data=strings_data)
    else:
        category_service.update_category(
            category_slug=current_category.slug, category_data=category_data, strings_data=strings_data
        )

    await state_service.safe_clear(state=state)

    await message_service.send_message(
        event=event, state=state, text=text, reply_markup=keyboard_generator.get_complete_action_keyboard()
    )


@admin_category_router.callback_query(CategoryCallbackFactory.filter(F.action == MenuActionEnum.REMOVE))
async def remove_category_request_handler(
    callback: CallbackQuery, state: FSMContext, keyboard_generator: KeyboardGenerator, _: Locale
) -> None:
    await callback.answer()

    fsm_data = await state.get_data()
    category = CategorySchema(**fsm_data["category"])
    back_callback_str = CategoryCallbackFactory(action=MenuActionEnum.RETRIEVE, slug=category.slug).pack()

    text = _("admin_category_remove_request", name=category.name)

    kb = keyboard_generator.get_confirmation_keyboard(back_callback_str=back_callback_str)

    await state.set_state(RemoveCategoryStates.wait_confirmation)
    await callback.message.answer(text=text, reply_markup=kb)


@admin_category_router.callback_query(
    ConfirmMenuCallbackFactory.filter(),
    StateFilter(RemoveCategoryStates.wait_confirmation),
)
async def remove_category_handler(
    callback: CallbackQuery,
    state: FSMContext,
    category_service: CategoryService,
    users: dict[str, dict[str, Any]],
    user_service: UserService,
    state_service: StateService,
    keyboard_generator: KeyboardGenerator,
    _: Locale,
) -> None:
    await callback.answer()

    fsm_data = await state.get_data()
    category = CategorySchema(**fsm_data["category"])

    related_users = [user_id for user_id in users if users[user_id]["category"] == category.slug]
    if len(related_users):
        user_service.remove_users(user_ids=related_users)

    category_service.remove_category(category_slug=category.slug)

    await callback.message.answer(
        text=_("admin_category_successfully_removed", name=category.name),
        reply_markup=keyboard_generator.get_complete_action_keyboard(),
    )
