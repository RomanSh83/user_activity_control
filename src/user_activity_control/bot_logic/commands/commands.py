from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats

from user_activity_control.bot_logic.enums.command_enums import AdminCommandEnum, CommonCommandEnum
from user_activity_control.infra.locale.types import LocaleFactory


async def set_commands(bot: Bot, _: LocaleFactory) -> None:
    chat_commands = [
        BotCommand(command=CommonCommandEnum.ABOUT, description=_("command_about")),
    ]
    admin_commands = [
        BotCommand(command=CommonCommandEnum.ABOUT, description=_("command_about")),
        BotCommand(command=AdminCommandEnum.START, description=_("command_start")),
    ]
    await bot.set_my_commands(chat_commands, scope=BotCommandScopeAllGroupChats())
    await bot.set_my_commands(admin_commands, scope=BotCommandScopeAllPrivateChats())
