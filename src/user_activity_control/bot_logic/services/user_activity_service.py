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
    def __init__(self, storage: ActivityStorage, text_composer: TextComposerService, logger_factory: LoggerFactory):
        self.storage = storage
        self.text_composer = text_composer
        self.logger = logger_factory(__name__)

    async def _send_delayed_message(self, message: Message, user: UserSchema, string_type: StringsTypesEnum) -> None:
        await asyncio.sleep(user.stand_down_delay * 60)
        await self._send_message(message=message, user=user, string_type=string_type)

    async def _send_message(self, message: Message, user: UserSchema, string_type: StringsTypesEnum) -> None:
        msg = self.text_composer.compose_text(user=user, string_type=string_type)
        if not msg:
            return
        await message.answer(msg)

    async def _create_stand_down_task(
        self, message: Message, user: UserSchema, string_type: StringsTypesEnum
    ) -> asyncio.Task | None:
        if user.stand_down_delay != 0:
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

    async def proceed_activity(self, message: Message, user: UserSchema, is_command: bool = False) -> None:
        storage_key = f"{user.user_id}:{message.chat.id}"
        last_activity_data = self.storage.pull_data(key=storage_key)

        # Если нужно дать ответ на команду - даем ответ и далее обрабатываем по алгоритму активность
        if is_command:
            await self._send_message(message=message, user=user, string_type=StringsTypesEnum.COMMAND)

        # Если в хранилище нет записей по активностям данного пользователя, или
        # время с последней активности больше заданного, отправляем сообщение о тревоге
        if (
            not last_activity_data
            or datetime.now(UTC).timestamp() - last_activity_data[ActivityKeysEnum.ACTIVITY_TIMESTAMP]
            > user.inactivity_alert_delay * 60
        ):
            self.logger.debug(msg=f"User: {user.user_id}. New activity detected after timeout. Sending alert message.")
            await self._send_message(message=message, user=user, string_type=StringsTypesEnum.ALARM)

        # Если время меньше выдержки и есть незавершенное задание на отбой - отменяем его
        elif not last_activity_data[ActivityKeysEnum.TASK].done():
            msg = f"User: {user.user_id}. New activity detected: current task cancelled, new task assigned."
            self.logger.debug(msg=msg)
            last_activity_data[ActivityKeysEnum.TASK].cancel(msg=msg)

        # Если это первая активность и записей в хранилище нет или нет активной задачи на отбой:
        if not last_activity_data or last_activity_data[ActivityKeysEnum.TASK].done():
            task = await self._create_stand_down_task(
                message=message, user=user, string_type=StringsTypesEnum.STAND_DOWN
            )
        else:  # иначе - оставляем активную задачу
            task = last_activity_data[ActivityKeysEnum.TASK]

        # Обновляем информацию в хранилище
        await self._update_last_activity(action_timestamp=datetime.now(UTC), key=storage_key, task=task)
