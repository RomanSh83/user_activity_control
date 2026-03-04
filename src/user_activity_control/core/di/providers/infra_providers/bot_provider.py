from aiogram import Bot, Dispatcher
from dishka import Provider, Scope, provide
from dynaconf import Dynaconf

from user_activity_control.infra.telegram.bot_core import BotCore


class BotProvider(Provider):
    @provide(scope=Scope.APP)
    def get_bot_core(self, settings: Dynaconf) -> BotCore:
        return BotCore(settings=settings)

    @provide(scope=Scope.APP)
    def get_bot(self, bot_core: BotCore) -> Bot:
        return bot_core.bot

    @provide(scope=Scope.APP)
    def get_dp(self, bot_core: BotCore) -> Dispatcher:
        return bot_core.dp
