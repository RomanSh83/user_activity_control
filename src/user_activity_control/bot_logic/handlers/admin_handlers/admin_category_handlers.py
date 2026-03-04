import uuid
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from dishka import FromDishka
from dynaconf import Dynaconf

from user_activity_control.bot_logic.callback_classes.category_callbacks import CategoryCallbackFactory
from user_activity_control.bot_logic.callback_classes.common_menu_callbacks import (
    ConfirmMenuCallbackFactory,
    SkipMenuCallbackFactory,
)
from user_activity_control.bot_logic.enums.entity_enums import CategoryEnum
from user_activity_control.bot_logic.enums.menu_enums import MenuActionEnum
from user_activity_control.bot_logic.filters.permission_filters import AdminFilter
from user_activity_control.bot_logic.keyboards.keyboard_generator import KeyboardGenerator
from user_activity_control.bot_logic.schemas.category_schemas import (
    CategoriesSchema,
    CategoryParamsUpdateSchema,
    CategorySchema,
)
from user_activity_control.bot_logic.services.category_services import CategoryService
from user_activity_control.bot_logic.services.user_services import UserService
from user_activity_control.bot_logic.states.category_states import (
    CreateCategoryStates,
    RemoveCategoryStates,
    UpdateCategoryStates,
)
from user_activity_control.bot_logic.validators.category_validators import CategoryValidator
from user_activity_control.core.enums.enums import ExamplesFilesEnum, ProjectFoldersEnum, StringsFilesEnum
from user_activity_control.infra.locale.types import LocaleFactory
from user_activity_control.infra.telegram.bot_services.message_service import MessageService
from user_activity_control.infra.telegram.bot_services.state_services import StateService

admin_category_router = Router()
admin_category_router.callback_query.filter(AdminFilter())


@admin_category_router.callback_query(
    CategoryCallbackFactory.filter(F.action.in_((MenuActionEnum.LIST, MenuActionEnum.CHOICE_LIST)))
)
async def list_categories_handler(
    callback: CallbackQuery,
    callback_data: CategoryCallbackFactory,
    state: FSMContext,
    settings: FromDishka[Dynaconf],
    categories: FromDishka[CategoriesSchema],
    keyboard_generator: FromDishka[KeyboardGenerator],
    category_service: FromDishka[CategoryService],
    message_service: FromDishka[MessageService],
    state_service: FromDishka[StateService],
    _: FromDishka[LocaleFactory],
) -> None:
    await callback.answer()

    back_callback_str = (
        await state_service.push_current_callback(state=state, callback_data=callback_data)
        if callback_data.action == MenuActionEnum.LIST
        else await state_service.pull_previous_callback(state=state)
    )

    limit = settings.PAGINATION_LIMIT

    page = callback_data.page if callback_data.page else 0
    categories_total = callback_data.total if callback_data.total else len(categories.root)

    paginated_callback_data = CategoryCallbackFactory(action=callback_data.action, page=page, total=categories_total)
    current_categories = category_service.get_categories(offset=callback_data.page * limit, limit=limit)
    text = _("admin_category_list") if categories_total != 0 else _("admin_category_list_empty")

    await message_service.send_message(
        event=callback,
        state=state,
        text=text,
        reply_markup=keyboard_generator.get_category_list_keyboard(
            categories=current_categories, callback_data=paginated_callback_data, back_callback_str=back_callback_str
        ),
    )


@admin_category_router.callback_query(CategoryCallbackFactory.filter(F.action == MenuActionEnum.RETRIEVE))
async def retrieve_category_handler(
    callback: CallbackQuery,
    callback_data: CategoryCallbackFactory,
    state: FSMContext,
    keyboard_generator: FromDishka[KeyboardGenerator],
    category_service: FromDishka[CategoryService],
    message_service: FromDishka[MessageService],
    state_service: FromDishka[StateService],
    _: FromDishka[LocaleFactory],
) -> None:
    await callback.answer()

    if callback_data.category_id is None:  # заглушка mypy
        return

    back_callback_str = await state_service.push_current_callback(state=state, callback_data=callback_data)

    category = category_service.get_category(category_id=callback_data.category_id)

    await state.update_data(category=category.model_dump())

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
    state: FSMContext,
    settings: FromDishka[Dynaconf],
    keyboard_generator: FromDishka[KeyboardGenerator],
    message_service: FromDishka[MessageService],
    state_service: FromDishka[StateService],
    _: FromDishka[LocaleFactory],
) -> None:
    await callback.answer()

    back_callback_str = await state_service.pull_previous_callback(state=state)

    if callback_data.action == MenuActionEnum.CREATE:
        text = _("admin_category_create_name", max_length=settings.MAX_CATEGORY_NAME_LENGTH)
        skip_button = False
        new_state = CreateCategoryStates.wait_name
    else:
        fsm_data = await state.get_data()
        category = CategorySchema(**fsm_data["category"])
        text = _("admin_category_update_name", name=category.name, max_length=settings.MAX_CATEGORY_NAME_LENGTH)
        skip_button = True
        new_state = UpdateCategoryStates.wait_name

    kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=skip_button)
    await state.set_state(new_state)
    await message_service.send_message(event=callback, state=state, text=text, reply_markup=kb)


@admin_category_router.message(StateFilter(CreateCategoryStates.wait_name, UpdateCategoryStates.wait_name))
@admin_category_router.callback_query(SkipMenuCallbackFactory.filter(), StateFilter(UpdateCategoryStates.wait_name))
async def create_update_category_name_handler(
    event: Message | CallbackQuery,
    state: FSMContext,
    category_validator: FromDishka[CategoryValidator],
    keyboard_generator: FromDishka[KeyboardGenerator],
    message_service: FromDishka[MessageService],
    state_service: FromDishka[StateService],
    base_dir: FromDishka[Path],
    _: FromDishka[LocaleFactory],
) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()

    back_callback_str = await state_service.pull_previous_callback(state=state)

    category_data = {}
    document = FSInputFile(
        base_dir / ProjectFoldersEnum.APP_DATA / ProjectFoldersEnum.EXAMPLES / ExamplesFilesEnum.TEMPLATES
    )

    if await state.get_state() == CreateCategoryStates.wait_name:
        text = _("admin_category_create_template_file")
        skip_button = False
        new_state = CreateCategoryStates.wait_template_file

    else:
        fsm_data = await state.get_data()
        current_category = CategorySchema(**fsm_data["category"])
        file_path = (
            base_dir
            / ProjectFoldersEnum.APP_DATA
            / ProjectFoldersEnum.STRINGS
            / current_category.category_id
            / StringsFilesEnum.TEMPLATES
        )
        if Path.exists(file_path):
            document = FSInputFile(file_path)
            text = _("admin_category_update_template_file_exists")
            skip_button = True
            new_state = UpdateCategoryStates.wait_optional_template_file
        else:
            text = _("admin_category_update_template_file_not_exists")
            skip_button = False
            new_state = UpdateCategoryStates.wait_required_template_file

    kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=skip_button)

    if isinstance(event, Message):
        name, validate_error_text = await category_validator.validate_name(value=event.text)
        if validate_error_text:
            await message_service.send_message(event=event, state=state, text=validate_error_text, reply_markup=kb)
            return
        category_data[CategoryEnum.NAME] = name

    await state.update_data(category_data=category_data)
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
    category_validator: FromDishka[CategoryValidator],
    keyboard_generator: FromDishka[KeyboardGenerator],
    message_service: FromDishka[MessageService],
    state_service: FromDishka[StateService],
    base_dir: FromDishka[Path],
    _: FromDishka[LocaleFactory],
) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()

    back_callback_str = await state_service.pull_previous_callback(state=state)

    fsm_data = await state.get_data()
    strings_data = {}
    document = FSInputFile(
        base_dir / ProjectFoldersEnum.APP_DATA / ProjectFoldersEnum.EXAMPLES / ExamplesFilesEnum.ALARM
    )

    if await state.get_state() == CreateCategoryStates.wait_template_file:
        text = _("admin_category_create_alarm_file")
        new_state = CreateCategoryStates.wait_alarm_file

    else:
        current_category = CategorySchema(**fsm_data["category"])
        file_path = (
            base_dir
            / ProjectFoldersEnum.APP_DATA
            / ProjectFoldersEnum.STRINGS
            / current_category.category_id
            / StringsFilesEnum.ALARM
        )
        if Path.exists(file_path):
            document = FSInputFile(file_path)
            text = _("admin_category_update_alarm_file_exists")
        else:
            text = _("admin_category_update_alarm_file_not_exists")
        new_state = UpdateCategoryStates.wait_alarm_file

    kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)

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
    category_validator: FromDishka[CategoryValidator],
    keyboard_generator: FromDishka[KeyboardGenerator],
    message_service: FromDishka[MessageService],
    state_service: FromDishka[StateService],
    base_dir: FromDishka[Path],
    _: FromDishka[LocaleFactory],
) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()

    back_callback_str = await state_service.pull_previous_callback(state=state)

    fsm_data = await state.get_data()
    strings_data = fsm_data.get("strings_data")
    document = FSInputFile(
        base_dir / ProjectFoldersEnum.APP_DATA / ProjectFoldersEnum.EXAMPLES / ExamplesFilesEnum.STAND_DOWN
    )

    if await state.get_state() == CreateCategoryStates.wait_alarm_file:
        text = _("admin_category_create_stand_down_file")
        new_state = CreateCategoryStates.wait_stand_down_file

    else:
        current_category = CategorySchema(**fsm_data["category"])
        file_path = (
            base_dir
            / ProjectFoldersEnum.APP_DATA
            / ProjectFoldersEnum.STRINGS
            / current_category.category_id
            / StringsFilesEnum.STAND_DOWN
        )
        if Path.exists(file_path):
            document = FSInputFile(file_path)
            text = _("admin_category_update_stand_down_file_exists")
        else:
            text = _("admin_category_update_stand_down_file_not_exists")
        new_state = UpdateCategoryStates.wait_stand_down_file

    kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)

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
    category_validator: FromDishka[CategoryValidator],
    keyboard_generator: FromDishka[KeyboardGenerator],
    message_service: FromDishka[MessageService],
    state_service: FromDishka[StateService],
    base_dir: FromDishka[Path],
    _: FromDishka[LocaleFactory],
) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()

    back_callback_str = await state_service.pull_previous_callback(state=state)

    fsm_data = await state.get_data()
    strings_data = fsm_data.get("strings_data")
    document = FSInputFile(
        base_dir / ProjectFoldersEnum.APP_DATA / ProjectFoldersEnum.EXAMPLES / ExamplesFilesEnum.COMMAND
    )

    if await state.get_state() == CreateCategoryStates.wait_stand_down_file:
        text = _("admin_category_create_command_file")
        new_state = CreateCategoryStates.wait_command_file

    else:
        current_category = CategorySchema(**fsm_data["category"])
        file_path = (
            base_dir
            / ProjectFoldersEnum.APP_DATA
            / ProjectFoldersEnum.STRINGS
            / current_category.category_id
            / StringsFilesEnum.COMMAND
        )
        if Path.exists(file_path):
            document = FSInputFile(file_path)
            text = _("admin_category_update_command_file_exists")
        else:
            text = _("admin_category_update_command_file_not_exists")
        new_state = UpdateCategoryStates.wait_command_file

    kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)

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
    category_validator: FromDishka[CategoryValidator],
    category_service: FromDishka[CategoryService],
    keyboard_generator: FromDishka[KeyboardGenerator],
    message_service: FromDishka[MessageService],
    state_service: FromDishka[StateService],
    _: FromDishka[LocaleFactory],
) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()

    back_callback_str = await state_service.pull_previous_callback(state=state)

    fsm_data = await state.get_data()
    category_data = fsm_data["category_data"]
    strings_data = fsm_data["strings_data"]

    if await state.get_state() == CreateCategoryStates.wait_command_file:
        category_id = str(uuid.uuid4())
        text = _("admin_category_created_successfully", name=category_data[CategoryEnum.NAME])
    else:
        current_category = CategorySchema(**fsm_data["category"])
        category_id = current_category.category_id
        text = _("admin_category_updated_successfully", name=current_category.name)

    kb = keyboard_generator.get_add_edit_keyboard(back_callback_str=back_callback_str, skip_button=True)

    if isinstance(event, Message):
        command, validate_error_text = await category_validator.validate_strings_file(message=event)
        if validate_error_text:
            await message_service.send_message(event=event, state=state, text=validate_error_text, reply_markup=kb)
            return
        strings_data["command"] = command

    if await state.get_state() == CreateCategoryStates.wait_command_file:
        category_service.create_category(
            category=CategorySchema(category_id=category_id, **fsm_data["category_data"]), strings_data=strings_data
        )
    else:
        category_service.update_category(
            category_id=category_id,
            category_data=CategoryParamsUpdateSchema(**category_data),
            strings_data=strings_data,
        )

    await state_service.safe_clear(state=state)

    await message_service.send_message(
        event=event, state=state, text=text, reply_markup=keyboard_generator.get_complete_action_keyboard()
    )


@admin_category_router.callback_query(CategoryCallbackFactory.filter(F.action == MenuActionEnum.REMOVE))
async def remove_category_request_handler(
    callback: CallbackQuery,
    state: FSMContext,
    keyboard_generator: FromDishka[KeyboardGenerator],
    message_service: FromDishka[MessageService],
    state_service: FromDishka[StateService],
    _: FromDishka[LocaleFactory],
) -> None:
    await callback.answer()

    back_callback_str = await state_service.pull_previous_callback(state=state)

    fsm_data = await state.get_data()
    category = CategorySchema(**fsm_data["category"])

    text = _("admin_category_remove_request", name=category.name)
    kb = keyboard_generator.get_confirmation_keyboard(back_callback_str=back_callback_str)

    await state.set_state(RemoveCategoryStates.wait_confirmation)

    await message_service.send_message(event=callback, state=state, text=text, reply_markup=kb)


@admin_category_router.callback_query(
    ConfirmMenuCallbackFactory.filter(),
    StateFilter(RemoveCategoryStates.wait_confirmation),
)
async def remove_category_handler(
    callback: CallbackQuery,
    state: FSMContext,
    category_service: FromDishka[CategoryService],
    user_service: FromDishka[UserService],
    message_service: FromDishka[MessageService],
    keyboard_generator: FromDishka[KeyboardGenerator],
    _: FromDishka[LocaleFactory],
) -> None:
    await callback.answer()

    fsm_data = await state.get_data()
    category = CategorySchema(**fsm_data["category"])

    related_users = user_service.get_category_user_ids(category_id=category.category_id)
    if len(related_users):
        user_service.remove_users(user_ids=related_users)

    category_service.remove_category(category_id=category.category_id)

    await message_service.send_message(
        event=callback,
        state=state,
        text=_("admin_category_successfully_removed", name=category.name),
        reply_markup=keyboard_generator.get_complete_action_keyboard(),
    )
