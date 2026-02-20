from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from user_activity_control.bot_logic.schemas.control_user_schemas import ControlUserSchema
from user_activity_control.bot_logic.schemas.user_schemas import UsersSchema


class ChatUserFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, users: UsersSchema) -> bool | dict[str, ControlUserSchema]:
        user_id = str(event.from_user.id)
        message = event if isinstance(event, Message) else event.message
        chat_id = str(message.chat.id) if hasattr(message, "chat") else None

        if user_id in users.root and chat_id and chat_id in users.root[user_id].chat_ids:
            return {"control_user": ControlUserSchema(id=event.from_user.id, **users.root[user_id])}
        return False
