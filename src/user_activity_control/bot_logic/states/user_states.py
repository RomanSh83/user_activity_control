from aiogram.fsm.state import State, StatesGroup


class CreateUserStates(StatesGroup):
    wait_id = State()
    wait_category = State()
    wait_chat_ids = State()
    wait_inactivity_alert_delay = State()
    wait_stand_down_delay = State()
    wait_unique_command_reactions = State()


class UpdateUserStates(StatesGroup):
    wait_id = State()
    wait_category = State()
    wait_chat_ids = State()
    wait_inactivity_alert_delay = State()
    wait_stand_down_delay = State()
    wait_unique_command_reactions = State()


class RemoveUserStates(StatesGroup):
    wait_confirmation = State()
