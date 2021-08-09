from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, inline_keyboard
from keyboards.inline import callback_data

from keyboards.inline.callback_data import start_edit_callback, gender_callback, avatar_callback

edit_start = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Начать игру', callback_data=start_edit_callback.new(start='yes')),
        InlineKeyboardButton(
            text='Изменить данные', callback_data=start_edit_callback.new(start='no'))
    ]
])


gender_choice = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Мужчина', callback_data=gender_callback.new(sex='Мужчина')),
        InlineKeyboardButton(
            text='Женщина', callback_data=gender_callback.new(sex='Женщина'))
    ]
])

avatar_choice = InlineKeyboardMarkup(row_width=3,
                                     inline_keyboard=[
                                         [
                                             InlineKeyboardButton(
                                                 text='1', callback_data=avatar_callback.new(number='1')),
                                             InlineKeyboardButton(
                                                 text='2', callback_data=avatar_callback.new(number='2')),
                                             InlineKeyboardButton(
                                                 text='3', callback_data=avatar_callback.new(number='3')),
                                         ]
                                     ])
