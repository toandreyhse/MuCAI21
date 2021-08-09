from aiogram.dispatcher.filters.state import StatesGroup, State


class ProfileState(StatesGroup):
    Nickname = State()
    Code = State()
    Birthday = State()
    Gender = State()
    Avatar = State()
