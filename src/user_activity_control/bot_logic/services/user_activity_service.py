import asyncio
from datetime import UTC, datetime

from aiogram.types import Message

from user_activity_control.bot_logic.enums.activity_enums import ActivityKeysEnum
from user_activity_control.bot_logic.enums.strings_type_enums import StringsTypesEnum
from user_activity_control.bot_logic.schemas.user_schemas import UserSchema
from user_activity_control.bot_logic.services.text_composer_service import TextComposerService
from user_activity_control.infra.logger.types import LoggerFactory
from user_activity_control.infra.storage.in_memory_storage import ActivityStorage


class UserActivityService:
    def __init__(
        self, storage: ActivityStorage, text_composer: TextComposerService, logger_factory: LoggerFactory
    ) -> None:
        self.storage = storage
        self.text_composer = text_composer
        self.logger = logger_factory(__name__)

    async def _send_delayed_message(self, message: Message, user: UserSchema, string_type: StringsTypesEnum) -> None:
        await asyncio.sleep(user.inactivity_alert_delay * 60)
        await self._send_message(message=message, user=user, string_type=string_type)

    async def _send_message(self, message: Message, user: UserSchema, string_type: StringsTypesEnum) -> None:
        msg = self.text_composer.compose_text(user=user, string_type=string_type)
        if not msg:
            return
        await message.answer(msg)

    async def _create_stand_down_task(
        self, message: Message, user: UserSchema, string_type: StringsTypesEnum
    ) -> asyncio.Task | None:
        if user.inactivity_alert_delay != 0:
            task = asyncio.create_task(
                self._send_delayed_message(message=message, user=user, string_type=string_type),
            )
            return task
        return None

    async def _update_last_activity(self, key: str, action_timestamp: datetime, task: asyncio.Task | None) -> None:
        self.storage.push_data(
            key=key,
            value={ActivityKeysEnum.ACTIVITY_TIMESTAMP: action_timestamp.timestamp(), ActivityKeysEnum.TASK: task},
        )

    async def proceed_command_activity(self, message: Message, user: UserSchema) -> None:
        self.logger.debug(msg=f"User {user.user_id}: Sending unique command reaction.")
        await self._send_message(message=message, user=user, string_type=StringsTypesEnum.COMMAND)
        await self.proceed_activity(message=message, user=user)

    async def proceed_activity(self, message: Message, user: UserSchema) -> None:
        # если сообщения о тревогах отключены, обработка не ведется
        if not user.alert_reactions:
            self.logger.debug(msg=f"User {user.user_id}: Activity ignored (reactions disabled).")
            return

        storage_key = f"{user.user_id}:{message.chat.id}"
        last_activity_data = self.storage.pull_data(key=storage_key) or {}
        task = last_activity_data.get(ActivityKeysEnum.TASK)

        # если обрабатывается первая активность или время с момента последней активности превысило установленный лимит
        # отправляем сообщение о тревоге
        if (
            not last_activity_data
            or datetime.now(UTC).timestamp() - last_activity_data[ActivityKeysEnum.ACTIVITY_TIMESTAMP]
            > user.inactivity_alert_delay * 60
        ):
            self.logger.debug(msg=f"User: {user.user_id}. New activity detected after timeout. Sending alert message.")
            await self._send_message(message=message, user=user, string_type=StringsTypesEnum.ALARM)

        # если сообщения об отбое включено
        if user.stand_down_reactions:
            # если существуют активные отложенные задачи на отправку сообщения - отменяем их
            if task and not task.done():
                msg = f"User {user.user_id}: Task replaced (new activity during timeout)."
                self.logger.debug(msg=msg)
                task.cancel(msg=msg)
            task = await self._create_stand_down_task(
                message=message, user=user, string_type=StringsTypesEnum.STAND_DOWN
            )

        # Обновляем информацию в хранилище
        await self._update_last_activity(action_timestamp=datetime.now(UTC), key=storage_key, task=task)
