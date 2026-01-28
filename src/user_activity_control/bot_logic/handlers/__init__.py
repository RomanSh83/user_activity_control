from aiogram import Router

from user_activity_control.bot_logic.handlers.chat_handlers import chat_router
from user_activity_control.bot_logic.handlers.service_handlers import service_router

main_router = Router()

main_router.include_router(service_router)
main_router.include_router(chat_router)
