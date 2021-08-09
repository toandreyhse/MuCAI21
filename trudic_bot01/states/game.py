from aiogram.dispatcher.filters.state import StatesGroup, State


class GameState(StatesGroup):
    StartGame = State()
    FirstGame = State()
    SecondGame = State()
    NewSession = State()
    NewSecondSession = State()
    NewGame = State()
    SecondGameProfileEdit = State()
    GetContact=State()
    FinishGame=State()


class DiscussState(StatesGroup):
    Message = State()
