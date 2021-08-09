from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_data import message_callback, event_data, start_new_game, update_tokens_callback
from keyboards.inline.callback_data import start_edit_callback


async def create_oponent_markup(balance, seconds):

    markup = InlineKeyboardMarkup(
        inline_keyboard=[

            [

                # InlineKeyboardButton(
                #     text=u'🙂', callback_data=message_callback.new(type='message', text='positive')),
                # InlineKeyboardButton(
                #     text=u'😶', callback_data=message_callback.new(type='message', text='netral')),
                # InlineKeyboardButton(
                #     text=u'🙁', callback_data=message_callback.new(type='message', text='negative'))\
                InlineKeyboardButton(
                    text=u'🙂', callback_data=message_callback.new(type='message', text='positive')),

                InlineKeyboardButton(
                    text=u'🙁', callback_data=message_callback.new(type='message', text='negative'))

            ],
            [
                InlineKeyboardButton(text='Написать партнеру',
                                     callback_data=message_callback.new(type='message', text='message_opponent')),
                InlineKeyboardButton(
                    text=u'😶', callback_data=message_callback.new(type='message', text='neutral')),
            ],


            [InlineKeyboardButton(
                text=f'итого токенов на вашем счете: {balance}', callback_data='balance'),
             ],
            [InlineKeyboardButton(
                text='кол-во токенов для текушего хода: 10', callback_data='money-10')
             ],
            [
                InlineKeyboardButton(
                    text='сохранить - keep', callback_data=event_data.new(choose='keep')),
                InlineKeyboardButton(
                    text='поделиться - share', callback_data=event_data.new(choose='share'))
            ],
            # [
            #     InlineKeyboardButton(text=seconds, callback_data='timer')
            # ],


            # [
            #     InlineKeyboardButton(text='Написать оппоненту',
            #                          callback_data=message_callback.new(type='message', text='message_opponent'))
            # ]
        ])

    return markup


async def create_oponent_markup_second(balance, tokens, seconds):

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [

                # InlineKeyboardButton(
                #     text=u'🙂', callback_data=message_callback.new(type='message', text='positive')),
                # InlineKeyboardButton(
                #     text=u'😶', callback_data=message_callback.new(type='message', text='netral')),
                # InlineKeyboardButton(
                #     text=u'🙁', callback_data=message_callback.new(type='message', text='negative'))\
                InlineKeyboardButton(
                    text=u'🙂', callback_data=message_callback.new(type='message', text='positive')),
                InlineKeyboardButton(
                    text=u'🙁', callback_data=message_callback.new(type='message', text='negative'))
            ],
            [
                InlineKeyboardButton(text='Написать партнеру',
                                     callback_data=message_callback.new(type='message', text='message_opponent')),
                InlineKeyboardButton(
                    text=u'😶', callback_data=message_callback.new(type='message', text='neutral'))
            ],


            [InlineKeyboardButton(
                text=f'итого токенов на вашем счете: {balance}', callback_data='balance'),
             ],
            [InlineKeyboardButton(
                text=f'кол-во токенов для текушего хода: {tokens}', callback_data='money-10')
             ],
            [

                InlineKeyboardButton(
                    text='-1', callback_data=update_tokens_callback.new(event='minus_1')),
                InlineKeyboardButton(
                    text='+1', callback_data=update_tokens_callback.new(event='plus_1')),
                InlineKeyboardButton(
                    text='+10', callback_data=update_tokens_callback.new(event='plus_10')),
                InlineKeyboardButton(
                    text='+20', callback_data=update_tokens_callback.new(event='plus_20')),
                InlineKeyboardButton(
                    text='+50', callback_data=update_tokens_callback.new(event='plus_50')),
            ],
            [
                InlineKeyboardButton(
                    text='сохранить - keep', callback_data=event_data.new(choose='keep')),
                InlineKeyboardButton(
                    text='поделиться - share', callback_data=event_data.new(choose='share'))
            ],



        ])

    return markup

new_session = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='начать следующую сессию', callback_data=start_edit_callback.new(start='yes'))
         ]
    ])


new_game = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Начать следующую игру', callback_data=start_new_game.new(start='new_game')),
    #         InlineKeyboardButton(
    #         text='Изменить данные', callback_data=start_edit_callback.new(start='no'))
    ]
])
