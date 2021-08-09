from handlers.users.game import show_opponent_info
from states.game import GameState
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery, InputFile, InputMediaPhoto, Message


from loader import dp, bot
from states import ProfileState


from keyboards.inline.profile_buttons import gender_choice, avatar_choice, edit_start

from keyboards.inline.callback_data import gender_callback, avatar_callback, start_edit_callback
from random import shuffle
from data.db.database import DBCommands
db = DBCommands()


@dp.message_handler(state=ProfileState.Nickname)
async def set_nickname(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['nickname'] = message.text
    await delete_messages(
        message, state, message.chat.id, message.message_id, 2)
    await ProfileState.Code.set()
    await message.answer('Придумайте персональный код (любые 4 цифры)')


@dp.message_handler(state=ProfileState.Code)
async def set_code(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['code'] = message.text
    await delete_messages(
        message, state, message.chat.id, message.message_id, 2)
    await ProfileState.Birthday.set()
    await message.answer('Введите дату рождения (дд.мм.гггг)')


@dp.message_handler(state=ProfileState.Birthday)
async def set_code(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['birthday'] = message.text
    await delete_messages(
        message, state, message.chat.id, message.message_id, 2)
    await ProfileState.Gender.set()
    await message.answer('Выберите пол', reply_markup=gender_choice)


@dp.callback_query_handler(gender_callback.filter(), state=ProfileState.Gender)
async def set_gender(call: CallbackQuery, callback_data: dict, state: FSMContext):
    gender = callback_data.get('sex')
    async with state.proxy() as data:
        data['gender'] = gender
    await call.message.edit_reply_markup()
    await delete_messages(
        call.message, state, call.message.chat.id, call.message.message_id, 1)
    await ProfileState.Avatar.set()
    for i in range(1, 4):
        await send_photo(call.message, call.message.chat.id, 'avatars', gender, i)
    await call.message.answer(text='Выберите аватар:', reply_markup=avatar_choice)


@dp.callback_query_handler(avatar_callback.filter(), state=ProfileState.Avatar)
async def avatar_set(call: CallbackQuery, callback_data: dict, state: FSMContext):
    avatar = callback_data.get('number')
    await call.message.edit_reply_markup()
    async with state.proxy() as data:
        data['avatar'] = avatar
        await db.add_user(call.message.chat.id, data['nickname'], data['code'], data['birthday'], data['gender'], avatar)
    await delete_messages(call.message.message_id, state, call.message.chat.id, call.message.message_id, 4)
    await show_user_data(call.message, call.message.chat.id)


@dp.callback_query_handler(start_edit_callback.filter(), state=GameState.StartGame)
async def start_game_or_edit_data(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()
    if callback_data['start'] == 'yes':

        # await db.etap_first(call.message.chat.id)
        # await db.game_first(call.message.chat.id)
        # await db.opponent_first(call.message.chat.id)
        await db.balance_null(call.message.chat.id)
        await GameState.FirstGame.set()
        await call.message.answer('Начинается первая игра.\n'
                                  '***\n'
                                  'С Вами будут играть 9 различных партнеров. Игра с каждым партнером состоит из 20 ходов. '
                                  'Во время каждого хода Вам будет дано по 10 игровых токенов и 3 секунды для принятия решения: '
                                  '"сохранить - keep" токены или "поделиться - share" токенами с данным партнером по игре. '
                                  'Вы можете коммуницировать с партнером, направлять ему смайлы и СМС.\n'
                                  '***\n'
                                  'Пожалуйста, Вы можете начать первую игру.')
        negative = ['keep', 'share', 'keep', 'keep', 'share', 'share', 'share', 'keep', 'share',
                                     'share', 'keep', 'keep', 'share', 'share', 'keep', 'share', 'keep', 'share', 'keep', 'keep']

        positive = ['share', 'share', 'share', 'share', 'keep', 'share', 'share', 'share', 'share',
                    'share', 'share', 'keep', 'share', 'share', 'share', 'share', 'keep', 'share', 'share', 'share']

        neutral = ['share', 'keep', 'share', 'share', 'keep', 'share', 'share', 'share', 'share', 'share', 'keep', 'share',
                                    'share', 'keep', 'share', 'share', 'share', 'keep', 'share', 'share']
        shuffle(positive)
        shuffle(negative)
        shuffle(neutral)
        user = await db.get_user(call.message.chat.id)
        opponents = [['Mr. A', 'Mr. B', 'Mr. C', 'R. 1', 'R. 2', 'R. 3', 'Rb. 1', 'Rb. 2', 'Rb. 3', ], [
            'Ms. X ', 'Ms. Y', 'Ms. Z', 'R. 1', 'R. 2', 'R. 3', 'Rb. 1', 'Rb. 2', 'Rb. 3']]
        async with state.proxy() as data:
            data['opponent_choose_negative'] = negative
            data['opponent_choose_neutral'] = neutral
            data['opponent_choose_positive'] = positive
            data['opponent_names'] = opponents[0] if user.gender == 'Мужчина' else opponents[1]
        await show_opponent_info(call, callback_data, user, state)
    else:
        await delete_messages(call.message, state, call.message.chat.id, call.message.message_id, 2)
        await ProfileState.Nickname.set()
        await call.message.answer('Введите свой ник')


async def show_user_data(message, user_id):
    user = await db.get_user(user_id)
    await send_photo(message, user.user_id, 'avatars', user.gender, user.avatar, 'Ваш аватар')
    await message.answer(f'Привет, {user.nickname}\nваши данные:\nкод: {user.code}\nдата рождения: {user.date_birth}\nпол: {user.gender}', reply_markup=edit_start)
    await GameState.StartGame.set()


async def delete_messages(message, state, chat_id, message_id, count):
    if count > 0 and count <= 1:
        await bot.delete_message(chat_id, message_id)
    else:
        for i in range(0, count):
            try:
                await bot.delete_message(chat_id, message_id-i)
            except:
                pass


async def send_photo(message,  chat_id, folder, gender, photo, caption=''):
    if caption:
        await bot.send_photo(chat_id, InputFile(f'assets/images/{folder}/{gender}/{photo}.png'), caption=caption)
    else:
        await bot.send_photo(chat_id, InputFile(f'assets/images/{folder}/{gender}/{photo}.png'))
