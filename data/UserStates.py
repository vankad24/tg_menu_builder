from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    """
    Класс для определения состояний Finite State Machine (FSM).
    """
    waitInput = State()
    State2 = State()
