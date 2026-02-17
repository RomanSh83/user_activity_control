from aiogram.fsm.state import State, StatesGroup


class CreateCategoryStates(StatesGroup):
    wait_name = State()
    wait_template_file = State()
    wait_command_file = State()
    wait_alarm_file = State()
    wait_stand_down_file = State()


class UpdateCategoryStates(StatesGroup):
    wait_name = State()
    wait_required_template_file = State()
    wait_optional_template_file = State()
    wait_command_file = State()
    wait_alarm_file = State()
    wait_stand_down_file = State()


class RemoveCategoryStates(StatesGroup):
    wait_confirmation = State()
