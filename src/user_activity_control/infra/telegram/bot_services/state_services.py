from aiogram.fsm.context import FSMContext

from user_activity_control.bot_logic.callback_classes.category_callbacks import CategoryCallbackFactory
from user_activity_control.bot_logic.callback_classes.common_menu_callbacks import (
    AdminMenuCallbackFactory,
    NoopCallbackFactory,
)
from user_activity_control.bot_logic.callback_classes.user_callbacks import UserCallbackFactory
from user_activity_control.bot_logic.enums.state_enums import StateKeysEnum
from user_activity_control.infra.logger.types import LoggerFactory


class StateService:
    def __init__(self, logger_factory: LoggerFactory):
        self.logger = logger_factory(__name__)

    @staticmethod
    async def safe_clear(state: FSMContext):
        fsm_data = await state.get_data()
        await state.set_data({StateKeysEnum.PREVIOUS_MSG_ID: fsm_data.get(StateKeysEnum.PREVIOUS_MSG_ID)})

    async def push_current_callback(
        self, state: FSMContext, callback_data: CategoryCallbackFactory | UserCallbackFactory | AdminMenuCallbackFactory
    ) -> str:
        """
        Сохранить текущий callback в стек.

        Сохраняет callback текущего шага в стек и возвращает callback предыдущего шага.
        Логика сохранения шагов в стеке:
            1. Для первого шага (если callback экземпляр класса AdminMenuCallbackFactory) формирует пустой стэк
            с сохранением первого шага AdminMenuCallbackFactory.
            2. Если текущий шаг не является следствием перехода по кнопкам навигации или кнопке "Предыдущий раздел" -
            сохраняет текущий шаг
            3. Если текущий шаг является следствием перехода по кнопке пагинации - заменяет вершину стека на текущий шаг
            4. Если текущий шаг является следствием перехода по кнопке "Предыдущий раздел" и на вершине стэка лежит
            текущий шаг (то есть возврат осуществлен с хэндлера, callback которого не был сохранен) - заменяет вершину
            стека на текущий шаг
            5. Если текущий шаг является следствием перехода по кнопке "Предыдущий раздел" - то удаляет два значения
            (шаг откуда осуществлен возврат и текущий шаг) с вершины стека и сохраняет текущий шаг


        """
        fsm_data = await state.get_data()
        callback_stack = fsm_data.get(StateKeysEnum.CALLBACK_STACK, [])

        if isinstance(callback_data, AdminMenuCallbackFactory):
            callback_stack = []
        else:
            if callback_stack and callback_data.pack() == callback_stack[-1]:
                callback_stack.pop()
            elif callback_stack and callback_data.by_paginate_button:
                callback_stack.pop()
            elif callback_data.by_previous_button:
                for _ in range(2):
                    if callback_stack:
                        callback_stack.pop()
            callback_data.by_previous_button = True
            callback_data.by_paginate_button = False

        back_callback_str = callback_stack[-1] if callback_stack else NoopCallbackFactory().pack()
        callback_stack.append(callback_data.pack())
        await state.update_data(callback_stack=callback_stack)

        return back_callback_str

    async def pull_previous_callback(self, state: FSMContext) -> str:
        fsm_data = await state.get_data()
        callback_stack = fsm_data.get(StateKeysEnum.CALLBACK_STACK, [])
        back_callback_str = callback_stack[-1] if len(callback_stack) > 0 else NoopCallbackFactory().pack()

        return back_callback_str
