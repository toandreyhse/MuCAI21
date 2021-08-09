from aiogram.types.callback_query import CallbackQuery
from aiogram.utils.callback_data import CallbackData

gender_callback = CallbackData('gender', 'sex')
avatar_callback = CallbackData('avatar', 'number')
start_edit_callback = CallbackData('game', 'start')
start_new_game = CallbackData('newgame', 'start')
message_callback = CallbackData('message', 'type', 'text')
event_data = CallbackData('event', 'choose')
update_tokens_callback = CallbackData('type', 'event') 
