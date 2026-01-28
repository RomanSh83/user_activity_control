import asyncio
from datetime import UTC, datetime

from aiogram.types import Message

from user_activity_control.bot_logic.enums.activity_enums import ActivityKeysEnum
from user_activity_control.bot_logic.enums.strings_type_enums import StringsTypesEnum
from user_activity_control.bot_logic.schemas.control_user_schemas import ControlUserSchema
from user_activity_control.bot_logic.services.text_composer_service import TextComposerService
from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_logger
from user_activity_control.infra.storage.in_memory_storage import ActivityStorage


class UserActivityService(Singleton):
    def __init__(self, storage: ActivityStorage, text_composer: TextComposerService):
        self.storage = storage
        self.text_composer = text_composer
        self.logger = get_logger(__name__)

    async def _send_delayed_message(self, message: Message, control_user: ControlUserSchema, string_type: str) -> None:
        await asyncio.sleep(control_user.stand_down_delay * 60)
        await self._send_message(message=message, control_user=control_user, string_type=string_type)

    async def _send_message(self, message: Message, control_user: ControlUserSchema, string_type: str) -> None:
        msg = self.text_composer.compose_text(control_user=control_user, string_type=string_type)
        if not msg:
            return
        await message.answer(msg)

    async def _create_stand_down_task(
        self, message: Message, control_user: ControlUserSchema, string_type: str
    ) -> asyncio.Task | None:
        if control_user.stand_down_delay != 0:
            task = asyncio.create_task(
                self._send_delayed_message(message=message, control_user=control_user, string_type=string_type),
            )
            return task
        return None

    async def _update_last_activity(self, user_id: int, action_timestamp: datetime, task: asyncio.Task | None) -> None:
        self.storage.push_data(
            key=user_id,
            value={ActivityKeysEnum.ACTIVITY_TIMESTAMP: action_timestamp.timestamp(), ActivityKeysEnum.TASK_ID: task},
        )

    async def proceed_activity(
        self, message: Message, control_user: ControlUserSchema, is_command: bool = False
    ) -> None:
        last_activity_data = self.storage.pull_data(key=control_user.id)

        # Если нужно дать ответ на команду - даем ответ и далее обрабатываем по алгоритму активность
        if is_command:
            await self._send_message(
                message=message, control_user=control_user, string_type=StringsTypesEnum.COMMAND.value
            )

        # Если в хранилище нет записей по активностям данного пользователя, или
        # время с последней активности больше заданного, отправляем сообщение о тревоге
        if (
            not last_activity_data
            or datetime.now(UTC).timestamp() - last_activity_data[ActivityKeysEnum.ACTIVITY_TIMESTAMP]
            > control_user.inactivity_alert_delay * 60
        ):
            self.logger.debug(
                msg=f"User: {control_user.id}. New activity detected after timeout. Sending alert message."
            )
            await self._send_message(
                message=message, control_user=control_user, string_type=StringsTypesEnum.ALARM.value
            )

        # Если время меньше выдержки и есть задание на отбой - отменяем его
        elif current_task := last_activity_data[ActivityKeysEnum.TASK_ID]:
            msg = f"User: {control_user.id}. New activity detected: current task cancelled, new task assigned."
            self.logger.debug(msg=msg)
            current_task.cancel(msg=msg)

        # Создаем новое задание на отбой
        task = await self._create_stand_down_task(
            message=message, control_user=control_user, string_type=StringsTypesEnum.STAND_DOWN.value
        )
        # Обновляем информацию в хранилище
        await self._update_last_activity(action_timestamp=datetime.now(UTC), user_id=control_user.id, task=task)
