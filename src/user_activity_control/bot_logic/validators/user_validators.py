from user_activity_control.bot_logic.services.user_services import UserService
from user_activity_control.infra.locale.types import LocaleFactory
from user_activity_control.infra.logger.types import LoggerFactory


class UserValidator:
    def __init__(self, logger_factory: LoggerFactory, user_service: UserService, _: LocaleFactory) -> None:
        self.logger = logger_factory(__name__)
        self.user_service = user_service
        self._ = _

    async def validate_id(self, value: str) -> tuple[None, str] | tuple[str, None]:
        try:
            id = int(value)
        except ValueError:
            return None, self._("validator_user_id_not_integer")

        if id <= 0:
            return None, self._("validator_user_id_not_positive")

        if self.user_service.exists_user(user_id=value):
            return None, self._("validator_user_id_already_exists")

        return value, None

    async def validate_chat_ids(self, value: str) -> tuple[None, str] | tuple[list[str], None]:
        try:
            chat_ids = [chat_id.strip() for chat_id in value.split(",") if chat_id.strip() and int(chat_id) != 0]
        except ValueError:
            return None, self._("validator_chat_ids_invalid_format")

        if len(chat_ids) == 0:
            return None, self._("validator_chat_ids_invalid_format")

        return chat_ids, None

    async def validate_inactivity_alert_delay(self, value: str) -> tuple[None, str] | tuple[int, None]:
        try:
            inactivity_alert_delay = int(value)
        except ValueError:
            return None, self._("validator_inactivity_alert_delay_invalid_format")

        if inactivity_alert_delay <= 0:
            return None, self._("validator_inactivity_alert_delay_not_positive")

        return inactivity_alert_delay, None
