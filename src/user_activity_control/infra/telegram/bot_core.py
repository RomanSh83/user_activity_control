from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dynaconf import Dynaconf


class BotCore:
    dp = Dispatcher()

    def __init__(self, settings: Dynaconf):
        self.settings = settings
        self.bot = Bot(token=self.settings.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
