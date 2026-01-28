from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats

from user_activity_control.bot_logic.enums.command_enums import ChatCommandEnum
from user_activity_control.infra.locale.types import Locale


async def set_commands(bot: Bot, _: Locale) -> None:
    chat_commands = [
        BotCommand(command=ChatCommandEnum.ABOUT, description=_("command_about")),
    ]
    await bot.set_my_commands(chat_commands, scope=BotCommandScopeAllGroupChats())
