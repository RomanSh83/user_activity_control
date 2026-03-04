from dishka import Provider, Scope, provide

from user_activity_control.infra.logger.types import LoggerFactory
from user_activity_control.infra.telegram.bot_services.message_service import MessageService
from user_activity_control.infra.telegram.bot_services.state_services import StateService


class BotServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def get_message_service(self) -> MessageService:
        return MessageService()

    @provide(scope=Scope.APP)
    def get_state_service(self, logger_factory: LoggerFactory) -> StateService:
        return StateService(logger_factory=logger_factory)
