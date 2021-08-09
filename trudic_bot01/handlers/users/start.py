from handlers.users.game import show_statistics
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
# from aiogram.types import InputFile
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup

from loader import dp, bot
from states import ProfileState

# from keyboards.inline.profile_buttons import edit_start
from handlers.users.profile import show_user_data

from states.game import GameState

from data.db.database import DBCommands, Message
db = DBCommands()


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    # await message.answer(f'Привет, {message.from_user.full_name}')
    user = await db.get_user(message.chat.id)
    if user:
        if user.game == 3:
            await message.answer('Вы уже завершили игру. Ваши результаты:')
            await show_statistics(message, user.user_id)
            await GameState.GetContact.set()
            contact_button = KeyboardButton(
                'Поделиться контактом', request_contact=True)
            contact_markup = ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True).add(contact_button)
            await message.answer('Поделитесь вашим контактом для участия в будущих иследованиях.', reply_markup=contact_markup)
        else:
            await show_user_data(message, user.user_id)
    else:
        await ProfileState.Nickname.set()
        await message.answer(f'Привет, {message.from_user.full_name}\nВведите свой ник')



