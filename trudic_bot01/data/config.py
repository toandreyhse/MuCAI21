import os

from dotenv import load_dotenv

# trudic_bot
BOT_TOKEN = 'Введите token бота'



DATABASE = str(os.getenv('DATABASE'))
PGUSER = str(os.getenv('PGUSER'))
PSPASSWORD = str(os.getenv('PSPASSWORD'))

host = str(os.getenv('host'))
