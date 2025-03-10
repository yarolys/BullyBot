from aiogram.fsm.state import StatesGroup, State


class FSM_admin_panel(StatesGroup):
    get_message = State()
    get_amount_of_dynamic_buttons = State()
    get_amount_of_dynamic_prompts = State()


class FSM_DynamicButtons(StatesGroup):
    delete_buttons = State()
    get_button_name = State()
    get_button_link = State()
    working_with_buttons = State()

class FSM_StaticButtons(StatesGroup):
    delete_buttons = State()
    get_button_name = State()
    get_button_link = State()
    working_with_buttons = State()

class FSM_Prompt(StatesGroup):
    delete_prompt = State()
    get_prompt_name = State()
    working_with_prompts = State()
    get_prompt_file = State()
    delete_user_prompt = State()
    get_user_prompt_name = State()
    working_user_with_prompts = State()
    get_user_prompt_file = State()
