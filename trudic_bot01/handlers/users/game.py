from asyncio import sleep
from typing import Text

from aiogram.types import ParseMode
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup

from keyboards.inline.game_buttons import create_oponent_markup, create_oponent_markup_second
from states import game
from states.game import GameState
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery, InputFile, InputMediaPhoto, Message, ContentType

from keyboards.inline.callback_data import event_data, message_callback, start_edit_callback, update_tokens_callback, start_new_game
from keyboards.inline.game_buttons import new_game, new_session

from loader import dp, bot

from random import shuffle
from tabulate import tabulate

from data.db.database import DBCommands
db = DBCommands()


async def add_message(message, user_id, user, message_text):
    await db.add_message(user_id, user, message_text)


async def add_game_events(message, user_id, event, oponent_event, tokens):
    await db.add_etap(user_id, event, oponent_event, tokens)


@ dp.message_handler(state=GameState.FirstGame)
async def message_for_oponents(message: Message, state: FSMContext):
    user = await db.get_user(message.chat.id)
    await message.answer('Сообщение отправлено партнеру')
    await db.add_message(user.user_id, 'yes', message.text)


@ dp.callback_query_handler(message_callback.filter(type='message'), state=GameState.FirstGame)
async def smile(call: CallbackQuery, callback_data: dict, state: FSMContext):
    user = await db.get_user(call.message.chat.id)
    if callback_data['text'] == 'positive':
        await call.message.answer(u'🙂')
        await db.add_message(user.user_id, 'yes', '🙂')
    elif callback_data['text'] == 'neutral':
        await call.message.answer(u'😶')
        await db.add_message(user.user_id, 'yes', '😶')
    elif callback_data['text'] == 'negative':
        await call.message.answer(u'🙁')
        await db.add_message(user.user_id, 'yes', '🙁')
    else:
        await call.message.answer("Введите сообщение:")


async def show_opponent_info(call, callback_data, user, state: FSMContext):
    user = await db.get_user(call.message.chat.id)
    number_gender = (0 if user.gender == 'Мужчина' else 1)
    balance = await db.get_balance(user.user_id)
    oponent_markup = await create_oponent_markup(user.balance, 3)
    smiles = [False, False, False, True, False, False, False, True, False,
              False, True, False, False, False, True, False, False, True, False, False]
    shuffle(smiles)
    async with state.proxy() as data:
        opponent = data['opponent_names']
        data['smiles'] = smiles
    if user.etap <= 1:
        await opponent_photo(call.message, user.user_id, 'opponents', user.gender, user.opponent, f'Ваш партнер {opponent[user.opponent-1]}', oponent_markup)
        await call.message.answer(f'{opponent[user.opponent-1]}: "Приветствую {user.nickname}"')
    else:
        await delete_messages(call.message, state, user.user_id, call.message.message_id, 1)
        await opponent_photo(call.message, user.user_id, 'opponents', user.gender, user.opponent, f'Ваш партнер {opponent[user.opponent-1]}', oponent_markup)


@dp.callback_query_handler(event_data.filter(), state=GameState.FirstGame)
async def keep_share(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=0)
    user = await db.get_user(call.message.chat.id)
    async with state.proxy() as data:
        if user.gender == 'Мужчина':
            if user.opponent in (1, 4, 8):
                choose = data['opponent_choose_negative']
            elif user.opponent in (2, 5, 7):
                choose = data['opponent_choose_neutral']
            elif user.opponent in (3, 6, 9):
                choose = data['opponent_choose_positive']
        elif user.gender == 'Женщина':
            if user.opponent in (2, 4, 8):
                choose = data['opponent_choose_negative']
            elif user.opponent in (3, 5, 7):
                choose = data['opponent_choose_neutral']
            elif user.opponent in (1, 6, 9):
                choose = data['opponent_choose_positive']
        smile = data['smiles']
        answer = choose[user.etap-1]
        opponent_name = data['opponent_names'][user.opponent-1]
    if callback_data['choose'] == 'keep':
        await add_game_events(call.message, user.user_id, 'keep', answer, 10)
        await db.update_balance(user.user_id, 10)
        await call.message.answer('токены сохранены')
        if answer == 'share':
            if smile[user.etap-1]:
                await call.message.answer(f'{opponent_name}:')
                await call.message.answer('🙁')
                await db.add_message(user.user_id, 'no', '🙁')
        else:
            if smile[user.etap-1]:
                await call.message.answer(f'{opponent_name}:')
                await call.message.answer(u'🙂')
                await db.add_message(user.user_id, 'no', '🙂')

    elif callback_data['choose'] == 'share':
        await call.message.answer('токены отправлены')
        if answer == 'share':
            await add_game_events(call.message, user.user_id, 'share', answer, 15)
            await call.message.answer('партнер вернул токены вам')
            await db.update_balance(user.user_id, 15)
            if smile[user.etap-1]:
                await call.message.answer(f'{opponent_name}:')
                await call.message.answer(u'🙂')
                await db.add_message(user.user_id, 'no', '🙂')

        else:
            await add_game_events(call.message, user.user_id, 'share', answer, 10)
            await call.message.answer('партнер оставил токены себе')
            await db.update_balance(user.user_id, 0)
            if smile[user.etap-1]:
                await call.message.answer(f'{opponent_name}:')
                await call.message.answer(u'🙂')
                await db.add_message(user.user_id, 'no', '🙂')

    await db.update_etap(user.user_id)
    if user.etap >= 20:
        await call.message.answer(f"{opponent_name}: до свидания, {user.nickname}")
        await db.new_opponent(user.user_id)
        if user.opponent >= 9:
            await call.message.edit_reply_markup()
            await GameState.NewGame.set()
            await call.message.answer(f'Первая игра окончена. Вы накопили {await db.get_balance(user.user_id)} токенов.', reply_markup=new_game)
            await db.new_game(user.user_id)
        else:
            await GameState.NewSession.set()
            await call.message.answer(f'{user.etap} ходов сессии с партнером {opponent_name} в {user.game}  игре сыграно. Всего на Вашем счету {await db.get_balance(user.user_id)} токенов.', reply_markup=new_session)
    else:
        await show_opponent_info(call, callback_data, user, state)


@dp.callback_query_handler(start_new_game.filter(), state=GameState.NewGame)
async def start_new_game(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()
    if callback_data['start'] == 'new_game':
        await db.etap_first(call.message.chat.id)
        await db.opponent_first(call.message.chat.id)
        await GameState.SecondGame.set()
        await call.message.answer('Начинается вторая игра. \n'
                                  '***\n'
                                  'Вам предлагается произвести действия в отношении 9 партнеров (из первой игры), а именно "сохранить - keep" токены или "поделиться - share" токенами, которые Вы накопили за первую игру. \n'
                                  'Всего у Вас будет 20 ходов (действий) в отношении каждого партнера, где Вам нужно самостоятельно выбрать кол-во игровых токенов (для хода) из кол-ва накопленных за первую игру только, у Вас будет 3 секунды для принятия решения: \n'
                                  '"сохранить - keep" токены или "поделиться - share" токенами с партнером. '
                                  'Партнер во второй игре не участвует, но Вы принимаете решение в его отношении, вспомните игровое поведение каждого из них, - и действуйте.\n'
                                  '***\n'
                                  'Пожалуйста, Вы можете начать вторую игру.')
        negative = ['keep', 'share', 'keep', 'keep', 'share', 'keep', 'keep', 'keep', 'keep',
                                     'keep', 'keep', 'keep', 'share', 'keep', 'keep', 'share', 'keep', 'share', 'keep', 'keep']

        positive = ['share', 'share', 'share', 'share', 'keep', 'share', 'share', 'share', 'share',
                    'share', 'share', 'keep', 'share', 'share', 'share', 'share', 'keep', 'share', 'share', 'share']

        neutral = ['share', 'keep', 'share', 'keep', 'keep', 'share', 'keep', 'share', 'keep', 'share', 'keep', 'share',
                                    'share', 'keep', 'share', 'keep', 'share', 'keep', 'share', 'keep']
        shuffle(positive)
        shuffle(negative)
        shuffle(neutral)
        async with state.proxy() as data:
            data['opponent_choose_negative'] = negative
            data['opponent_choose_neutral'] = neutral
            data['opponent_choose_positive'] = positive
            data['tokens'] = 1
        user = await db.get_user(call.message.chat.id)
        await show_opponent_info_for_second_game(call, callback_data, user, state,  tokens=data['tokens'])
    # if callback_data['start'] == 'no':
    #     await ProfileState.Nickname.set()
    #     await call.message.answer('Введите свой ник')
    #     await GameState.SecondGameProfileEdit.set()


@dp.callback_query_handler(start_edit_callback.filter(), state=GameState.NewSession)
async def start_new_session(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()
    if callback_data['start'] == 'yes':
        await GameState.FirstGame.set()
        await show_opponent_info(call, callback_data, call.message.chat.id, state)


async def opponent_photo(message,  chat_id, folder, gender, photo, caption='', reply_markup=None):
    if caption:
        await bot.send_photo(chat_id, InputFile(f'assets/images/{folder}/{gender}/{photo}.png'), caption=caption, reply_markup=reply_markup)
    else:
        await bot.send_photo(chat_id, InputFile(f'assets/images/{folder}/{gender}/{photo}.png'))


async def delete_messages(message, state, chat_id, message_id, count):
    try:
        if count > 0 and count <= 1:
            await bot.delete_message(chat_id, message_id)
        else:
            for i in range(0, count):
                await bot.delete_message(chat_id, message_id-i)
    except:
        print('Не удалось удалить сообщение.')


#####
#####
#####
##### GAME 2 ####


async def show_opponent_info_for_second_game(call, callback_data, user, state: FSMContext, tokens=1):
    user = await db.get_user(call.message.chat.id)
    opponents = [['Mr. A', 'Mr. B', 'Mr. C', 'R. 1', 'R. 2', 'R. 3', 'Rb. 1', 'Rb. 2', 'Rb. 3', ], [
        'Ms. X ', 'Ms. Y', 'Ms. Z', 'R. 1', 'R. 2', 'R. 3', 'Rb. 1', 'Rb. 2', 'Rb. 3']]
    number_gender = (0 if user.gender == 'Мужчина' else 1)
    # if user.etap == 1:
    #     await opponent_photo(call.message, call.message.chat.id, 'opponents', user.gender, user.opponent, 'Ваш оппонент')
    balance = await db.get_balance(user.user_id)
    # async with state.proxy() as data:
    #     tokens = data['tokens']
    smiles = [False, False, False, True, False, False, False, True, False,
              False, True, False, False, False, True, False, False, True, False, False]
    shuffle(smiles)
    async with state.proxy() as data:
        opponent = data['opponent_names']
        data['smiles'] = smiles
        data['tokens'] = tokens
    oponent_markup = await create_oponent_markup_second(user.balance, data['tokens'], 3)
    # await call.message.answer('Hello', oponent_markup)
    # await call.message.answer('oponent_markup')
    if user.etap <= 1:
        await opponent_photo(call.message, user.user_id, 'opponents', user.gender, user.opponent, f'Ваш партнер {opponent[user.opponent-1]}', oponent_markup)
        await call.message.answer(f'{opponent[user.opponent-1]}: "Приветствую {user.nickname}"')
    else:
        await delete_messages(call.message, state, user.user_id, call.message.message_id, 1)
        await opponent_photo(call.message, user.user_id, 'opponents', user.gender, user.opponent, f'Ваш партнер {opponent[user.opponent-1]}', oponent_markup)


@dp.callback_query_handler(update_tokens_callback.filter(), state=GameState.SecondGame)
async def change_tokens(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=0)
    user = await db.get_user(call.message.chat.id)
    async with state.proxy() as data:
        tokens = int(data['tokens'])
    if callback_data['event'] == 'minus_1':
        async with state.proxy() as data:
            if (tokens - 1) <= 0:
                data['tokens'] = 1
            else:
                data['tokens'] = tokens - 1
        await show_opponent_info_for_second_game(call, callback_data, call.message.chat.id, state, data['tokens'])
    elif callback_data['event'] == 'plus_1':
        async with state.proxy() as data:
            if data['tokens'] + 1 > user.balance:
                data['tokens'] = user.balance
            else:
                data['tokens'] = data['tokens'] + 1
        await show_opponent_info_for_second_game(call, callback_data, call.message.chat.id, state, data['tokens'])
    elif callback_data['event'] == 'plus_10':
        async with state.proxy() as data:
            if data['tokens'] + 10 > user.balance:
                data['tokens'] = user.balance
            else:
                data['tokens'] = data['tokens'] + 10
        await show_opponent_info_for_second_game(call, callback_data, call.message.chat.id, state, data['tokens'])
    elif callback_data['event'] == 'plus_20':
        async with state.proxy() as data:
            if data['tokens'] + 20 > user.balance:
                data['tokens'] = user.balance
            else:
                data['tokens'] = data['tokens'] + 20
        await show_opponent_info_for_second_game(call, callback_data, call.message.chat.id, state, data['tokens'])
    elif callback_data['event'] == 'plus_50':
        async with state.proxy() as data:
            if data['tokens'] + 50 > user.balance:
                data['tokens'] = user.balance
            else:
                data['tokens'] = data['tokens'] + 50
        await show_opponent_info_for_second_game(call, callback_data, call.message.chat.id, state, data['tokens'])


@dp.callback_query_handler(event_data.filter(), state=GameState.SecondGame)
async def keep_share_second(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=0)
    user = await db.get_user(call.message.chat.id)
    async with state.proxy() as data:
        choose = []
        if user.gender == 'Мужчина':
            if user.opponent in (1, 4, 8):
                choose = data['opponent_choose_negative']
            elif user.opponent in (2, 5, 7):
                choose = data['opponent_choose_neutral']
            elif user.opponent in (3, 6, 9):
                choose = data['opponent_choose_positive']
        elif user.gender == 'Женщина':
            if user.opponent in (2, 4, 8):
                choose = data['opponent_choose_negative']
            elif user.opponent in (3, 5, 7):
                choose = data['opponent_choose_neutral']
            elif user.opponent in (1, 6, 9):
                choose = data['opponent_choose_positive']
        smile = data['smiles']
        answer = choose[user.etap-1]
        opponent_name = data['opponent_names'][user.opponent-1]
        tokens = data['tokens']
    if callback_data['choose'] == 'keep':
        await add_game_events(call.message, user.user_id, 'keep', 'nothing', tokens)
        await call.message.answer('токены сохранены')
        # await db.update_balance(user.user_id, tokens)
        if answer == 'share':
            if smile[user.etap-1]:
                await call.message.answer(f'{opponent_name}:')
                await call.message.answer(u'🙁')
                await db.add_message(user.user_id, 'no', '🙁')
        else:
            if smile[user.etap-1]:
                await call.message.answer(f'{opponent_name}:')
                await call.message.answer(u'🙂')
                await db.add_message(user.user_id, 'no', '🙂')

    elif callback_data['choose'] == 'share':
        await call.message.answer('токены отправлены')
        if answer == 'share':
            await add_game_events(call.message, user.user_id, 'share', 'nothing', tokens)
            await db.update_balance(user.user_id, -tokens)
            if smile[user.etap-1]:
                await call.message.answer(f'{opponent_name}:')
                await call.message.answer(u'🙂')
                await db.add_message(user.user_id, 'no', '🙂')

        else:
            await add_game_events(call.message, user.user_id, 'share', 'nothing', tokens)
            await db.update_balance(user.user_id, -tokens)
            if smile[user.etap-1]:
                await call.message.answer(f'{opponent_name}:')
                await call.message.answer(u'🙂')
                await db.add_message(user.user_id, 'no', '🙂')

    await db.update_etap(user.user_id)
    if user.etap >= 20:
        await db.new_opponent(user.user_id)
        if user.opponent >= 9:
            await db.new_game(user.user_id)
            await call.message.edit_reply_markup()
            await GameState.SecondGame.set()
            await call.message.answer(f'Игра окончена!!!')
            await show_statistics(call.message, user.user_id)
            await GameState.GetContact.set()
            contact_button = KeyboardButton(
                'Поделиться контактом', request_contact=True)
            contact_markup = ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True).add(contact_button)
            await call.message.answer('Поделитесь вашим контактом для участия в будущих иследованиях.', reply_markup=contact_markup)
        else:
            await GameState.NewSecondSession.set()
            await call.message.answer(f'{user.etap} сессия {user.game} игры окончена. Всего Вы накопили {await db.get_balance(user.user_id)} токенов.', reply_markup=new_session)

    else:
        await show_opponent_info_for_second_game(call, callback_data, user, state)


@dp.callback_query_handler(start_edit_callback.filter(), state=GameState.NewSecondSession)
async def start_new_second_session(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()
    if callback_data['start'] == 'yes':
        await GameState.SecondGame.set()
        async with state.proxy() as data:
            tokens = data['tokens']
        await show_opponent_info_for_second_game(call, callback_data, call.message.chat.id, state, tokens)


@ dp.message_handler(state=GameState.SecondGame)
async def message_for_oponents(message: Message, state: FSMContext):
    await message.answer('Сообщение отправлено партнеру')


@ dp.callback_query_handler(message_callback.filter(type='message'), state=GameState.SecondGame)
async def smile(call: CallbackQuery, callback_data: dict, state: FSMContext):
    user = await db.get_user(call.message.chat.id)
    if callback_data['text'] == 'positive':
        await call.message.answer(u'🙂')
        await db.add_message(user.user_id, 'yes', '🙂')
    elif callback_data['text'] == 'neutral':
        await call.message.answer(u'😶')
        await db.add_message(user.user_id, 'yes', '😶')
    elif callback_data['text'] == 'negative':
        await call.message.answer(u'🙁')
        await db.add_message(user.user_id, 'yes', '🙁')
    else:
        await call.message.answer("Введите сообщение:")
        


async def show_statistics(message, user_id):
    user = await db.get_user(message.chat.id)
    answer = []
    opponents = [['Mr. A', 'Mr. B', 'Mr. C', 'R. 1', 'R. 2', 'R. 3', 'Rb. 1', 'Rb. 2', 'Rb. 3', ], [
        'Ms. X ', 'Ms. Y', 'Ms. Z', 'R. 1', 'R. 2', 'R. 3', 'Rb. 1', 'Rb. 2', 'Rb. 3']]
    number_gender = (0 if user.gender == 'Мужчина' else 1)
    for j in range(1, 10):
        game_answer = [j, opponents[number_gender][j-1]]
        for i in range(1, 3):
            token = await db.get_etap_result(user.user_id, i, j)
            game_answer.append(token)
        answer.append(game_answer)

    headers = ['№', 'партнер', '1 игра:', '2 игра:']
    text = tabulate(answer, headers)
    await message.answer(text)


@dp.message_handler(content_types=ContentType.CONTACT, state=GameState.GetContact)
async def bot2_echo(message: Message):
    await message.answer('Ваш контакт сохранен', reply_markup='')
    await db.add_contact(message.contact['user_id'], message.contact['phone_number'])
    await GameState.FinishGame.set()
    await message.answer('trudicbot - игра для людей и роботов\n'
                         'вопросы, предложения, обратная связь 👉 @trudicbot @cybiouralist  \n'
                         'поделится игрой с другом t.me/trudic_bot и @trudic_bot\n')


@dp.message_handler(state=GameState.FinishGame)
async def answer_after_all(message: Message):
    await message.answer('trudicbot - игра для людей и роботов\n'
                         'вопросы, предложения, обратная связь 👉 @trudicbot @cybiouralist  \n'
                         'поделится игрой с другом t.me/trudic_bot и @trudic_bot\n')
