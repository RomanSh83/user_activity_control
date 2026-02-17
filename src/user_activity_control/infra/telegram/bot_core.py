from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from user_activity_control.bot_logic.keyboards.keyboard_generator import KeyboardGenerator
from user_activity_control.bot_logic.services.admin_services.categories_services import CategoryService
from user_activity_control.bot_logic.services.admin_services.users_services import UserService
from user_activity_control.bot_logic.services.bot_services.send_message_service import MessageService
from user_activity_control.bot_logic.services.bot_services.state_services import StateService
from user_activity_control.bot_logic.services.text_composer_service import TextComposerService
from user_activity_control.bot_logic.services.user_activity_service import UserActivityService
from user_activity_control.bot_logic.validators.category_validators import CategoryValidator
from user_activity_control.bot_logic.validators.user_validators import UserValidator
from user_activity_control.core.config import (
    get_admins,
    get_base_dir,
    get_categories,
    get_settings,
    get_user_settings,
)
from user_activity_control.infra.bot_storage.in_memory_storage import ActivityStorage
from user_activity_control.infra.locale.locale_utils import get_translate_string


class BotCore:
    bot = Bot(token=get_settings().TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(
        settings=get_settings(),
        admins=get_admins(),
        base_dir=get_base_dir(),
        categories=get_categories(),
        category_validator=CategoryValidator(),
        category_service=CategoryService(),
        message_service=MessageService(),
        state_service=StateService(),
        text_composer=TextComposerService(),
        user_settings=get_user_settings(),
        user_service=UserService(),
        user_validator=UserValidator(),
        user_activity_service=UserActivityService(storage=ActivityStorage(), text_composer=TextComposerService()),
        activity_storage=ActivityStorage(),
        keyboard_generator=KeyboardGenerator(),
        _=get_translate_string,
    )


def get_bot() -> Bot:
    return BotCore.bot


def get_dp() -> Dispatcher:
    return BotCore.dp
