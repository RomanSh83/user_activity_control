from aiogram.fsm.context import FSMContext

from user_activity_control.bot_logic.enums.state_enums import StateKeysEnum
from user_activity_control.core.base.singleton import Singleton
from user_activity_control.core.config import get_logger


class StateService(Singleton):
    def __init__(self):
        self.logger = get_logger(__name__)

    @staticmethod
    async def safe_clear(state: FSMContext):
        fsm_data = await state.get_data()
        await state.set_data({StateKeysEnum.PREVIOUS_MSG_ID: fsm_data.get(StateKeysEnum.PREVIOUS_MSG_ID)})
