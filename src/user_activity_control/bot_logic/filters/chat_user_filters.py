from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from user_activity_control.bot_logic.enums.user_settings_enums import UserSettingsEnum
from user_activity_control.bot_logic.schemas.control_user_schemas import ControlUserSchema


class ChatUserFilter(BaseFilter):
    async def __call__(
        self, event: Message | CallbackQuery, user_settings: dict[str, dict[str, Any]]
    ) -> bool | dict[str, ControlUserSchema]:
        user_id = str(event.from_user.id)
        message = event if isinstance(event, Message) else event.message
        chat_id = str(message.chat.id) if hasattr(message, "chat") else None
        if user_id in user_settings and chat_id and chat_id in user_settings[user_id][UserSettingsEnum.CHAT_IDS]:
            return {"control_user": ControlUserSchema(id=event.from_user.id, **user_settings[user_id])}
        return False
