from aiogram.filters import BaseFilter
from aiogram.types import Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject


class AdminFilter(BaseFilter):
    @inject
    async def __call__(self, message: Message, admin_ids: FromDishka[set[str]]) -> bool:
        if isinstance(admin_ids, int):
            return message.from_user.id == admin_ids
        return message.from_user.id in admin_ids
