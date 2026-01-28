from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from user_activity_control.bot_logic.services.text_composer_service import TextComposerService
from user_activity_control.bot_logic.services.user_activity_service import UserActivityService
from user_activity_control.core.config import get_admins, get_base_settings, get_user_settings, get_user_types
from user_activity_control.infra.locale.locale_utils import get_translate_string
from user_activity_control.infra.storage.in_memory_storage import ActivityStorage


class BotCore:
    bot = Bot(token=get_base_settings().TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(
        admins=get_admins(),
        user_types=get_user_types(),
        user_settings=get_user_settings(),
        user_activity_service=UserActivityService(storage=ActivityStorage(), text_composer=TextComposerService()),
        activity_storage=ActivityStorage(),
        _=get_translate_string,
    )


def get_bot() -> Bot:
    return BotCore.bot


def get_dp() -> Dispatcher:
    return BotCore.dp
