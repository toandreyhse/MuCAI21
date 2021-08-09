from aiogram import executor
from loader import bot
from handlers import dp
from data.db.database import start_db
from utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    await set_default_commands(dp)
    await start_db()


async def on_shutdown(dp):
    await bot.close()

if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)
