from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, Message

from user_activity_control.bot_logic.enums.state_enums import StateKeysEnum


class MessageService:
    @staticmethod
    async def send_message(
        event: Message | CallbackQuery,
        state: FSMContext,
        text: str,
        document: FSInputFile | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ):
        """
        Функция отправки сообщения ботом в чат с пользователем.

        1. Если пользователь обращается к боту текстовым сообщением - то перед ответом это сообщение удаляется
        2. Если пользователь осуществляет переход нажатием на inline-кнопку,
           то ответ формируется в виде редактирования предыдущего сообщения.
        3. После отправки ответа, id сообщения сохраняется в fsm_state для последующего использования при ответах
        """

        bot = event.bot
        fsm_data = await state.get_data()
        previous_msg_id = fsm_data.get(StateKeysEnum.PREVIOUS_MSG_ID)

        # Удаляем входящее сообщение от пользователя, если это нажатие inline-кнопки и получаем chat_id
        if isinstance(event, Message):
            chat_id = event.chat.id
            with suppress(TelegramBadRequest):
                await event.delete()
        else:
            chat_id = event.message.chat.id

        answer_message = None

        # Если есть предыдущее сообщение и это не документ, пробуем ответить его редактированием
        if previous_msg_id and not document:
            with suppress(TelegramBadRequest):
                answer_message = await bot.edit_message_text(
                    chat_id=chat_id, message_id=previous_msg_id, text=text, reply_markup=reply_markup
                )

        # Если не удалось отредактировать сообщение - отвечаем отправкой нового,
        # предварительно удалив предыдущее если оно есть
        if not answer_message:
            if previous_msg_id:
                with suppress(TelegramBadRequest):
                    await bot.delete_message(chat_id, previous_msg_id)

            if document:
                answer_message = await bot.send_document(
                    chat_id=chat_id, document=document, caption=text, reply_markup=reply_markup
                )
            else:
                answer_message = await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

        # Сохраняем id последнего сообщения в state
        await state.update_data(previous_msg_id=answer_message.message_id)
