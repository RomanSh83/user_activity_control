from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from user_activity_control.bot_logic.schemas.user_schemas import UserSchema, UsersSchema


class ChatUserFilter(BaseFilter):
    @inject
    async def __call__(
        self, event: Message | CallbackQuery, users: FromDishka[UsersSchema]
    ) -> bool | dict[str, UserSchema]:
        user_id = str(event.from_user.id)
        message = event if isinstance(event, Message) else event.message
        chat_id = str(message.chat.id) if hasattr(message, "chat") else None

        if user_id in users.root and chat_id and chat_id in users.root[user_id].chat_ids:
            return {"user": UserSchema(user_id=user_id, **users.root[user_id].model_dump())}
        return False
