from aiogram.filters import BaseFilter
from aiogram.types import Message

from user_activity_control.core.config import get_admins


class AdminFilter(BaseFilter):
    def __init__(self) -> None:
        self.admin_ids = get_admins()

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.admin_ids, int):
            return message.from_user.id == self.admin_ids
        return message.from_user.id in self.admin_ids
