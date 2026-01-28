import asyncio

from user_activity_control.bot_logic.handlers import main_router
from user_activity_control.infra.telegram.bot_core import get_bot, get_dp

bot = get_bot()
dp = get_dp()


async def main() -> None:
    dp.include_router(main_router)
    async with bot:
        await dp.start_polling(bot)


def run_app() -> None:
    asyncio.run(main())
