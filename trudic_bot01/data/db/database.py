from aiogram import Bot, types
from aiogram.types.base import Boolean
from gino import Gino
import sqlalchemy
# from gino.schema import GinoSchemaVisitor
from sqlalchemy import (Column, Integer, BigInteger,
                        String, Sequence, DateTime, Boolean)
from sqlalchemy import sql
import asyncio
import datetime

from sqlalchemy.sql.functions import user

db = Gino()


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    nickname = Column(String(20))
    code = Column(Integer)
    date_birth = Column(String(15))
    gender = Column(String(10))
    avatar = Column(Integer)
    balance = Column(Integer, default=100)
    game = Column(Integer, default=1)
    opponent = Column(Integer, default=1)
    etap = Column(Integer, default=1)
    query: sql.Select

    def __repr__(self) -> str:
        return "<User(id='{}', nickname='{}', code='{}')>".format(self.id, self.nickname, self.code)


class Game(db.Model):
    __tablename__ = 'game'

    id = Column(Integer, Sequence('game_id'), primary_key=True)
    game_id = Column(Integer)
    user_id = Column(Integer)
    etap_id = Column(Integer)
    opponent_id = Column(Integer)
    user_balance = Column(Integer)
    event = Column(String(10))
    opponent_event = Column(String(10))
    tokens = Column(Integer)
    datetime = Column(DateTime, default=datetime.datetime.utcnow)


class Message(db.Model):
    __tablename__ = 'game_message'

    id = Column(Integer, Sequence('game_message_id'), primary_key=True)
    game_id = Column(Integer)
    etap_id = Column(Integer)
    user_id = Column(Integer)
    opponent_id = Column(Integer)
    user = Column(String(10))
    message = Column(String(100))
    time = Column(DateTime, default=datetime.datetime.utcnow)


class Contact(db.Model):
    __tablename__ = 'contact'
    id = Column(Integer, Sequence('contact_id'), primary_key=True)
    user_id = Column(Integer)
    phone_number = Column(String(20))


class DBCommands:
    async def get_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def add_user(self, user_id, nickname, code, date_birth, gender, avatar):
        new_user = await User.query.where(User.user_id == user_id).gino.first()
        if new_user:
            await new_user.update(nickname=nickname, code=int(code), date_birth=date_birth, gender=gender, avatar=int(avatar)).apply()
        else:
            new_user = User()
            new_user.user_id = user_id
            new_user.nickname = nickname
            new_user.code = int(code)
            new_user.date_birth = date_birth
            new_user.gender = gender
            new_user.avatar = int(avatar)
            await new_user.create()
        return new_user

    async def add_contact(self, user_id, phone_number):
        new_user = await Contact.query.where(Contact.user_id == user_id).gino.first()
        if new_user:
            await new_user.update(phone_number=phone_number).apply()
        else:
            new_contact = Contact()
            new_contact.user_id = user_id
            new_contact.phone_number = phone_number
            await new_contact.create()

    async def add_etap(self, user_id, event, opponent_event, tokens):
        new_etap = Game()
        m_user = await User.query.where(User.user_id == user_id).gino.first()
        new_etap.game_id = m_user.game
        new_etap.etap_id = m_user.etap
        new_etap.user_id = m_user.user_id
        new_etap.opponent_id = m_user.opponent
        new_etap.user_balance = m_user.balance
        new_etap.event = event
        new_etap.opponent_event = opponent_event
        new_etap.tokens = tokens
        await new_etap.create()
        return new_etap

    async def add_message(self, user_id, user, message):
        new_message = Message()
        m_user = await User.query.where(User.user_id == user_id).gino.first()
        new_message.game_id = m_user.game
        new_message.user_id = m_user. user_id
        new_message.etap_id = m_user.etap
        new_message.opponent_id = m_user.opponent
        new_message.user = user
        new_message.message = message
        await new_message.create()
        return new_message

    async def get_etap_result(self, user_id, game_id, opponent_id):
        result = await Game.query.where(Game.user_id == user_id).where(Game.game_id == game_id).where(Game.opponent_id == opponent_id).where(Game.etap_id == 20).gino.first()
        tokens = result.user_balance
        if result.event == 'share' and result.opponent_event == 'keep':
            tokens = result.user_balance - result.tokens
        elif result.event == 'share' and result.opponent_event == 'share':
            tokens = result.user_balance + result.tokens
        elif result.event == 'keep' and result.opponent_event == 'share':
            tokens = result.user_balance + result.tokens
        elif result.event == 'share' and result.opponent_event == 'nothing':
            tokens = result.user_balance - result.tokens
        elif result.event == 'keep' and result.opponent_event == 'nothing':
            tokens = result.user_balance
        return tokens

    async def get_balance(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user.balance

    async def etap_first(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        await user.update(etap=1).apply()
        return user

    async def game_first(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        await user.update(game=1).apply()
        return user

    async def opponent_first(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        await user.update(opponent=1).apply()
        return user

    async def balance_null(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        await user.update(balance=0).apply()
        return user

    async def update_game(self, user_id, game):
        user = await User.query.where(User.user_id == user_id).gino.first()
        new_game = user.game + 1
        await user.update(game=new_game).apply()
        return user

    async def update_opponent(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        new_opponent = user.opponent + 1
        await user.update(opponent=new_opponent).apply()
        return user

    async def update_etap(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        new_etap = user.etap + 1
        await user.update(etap=new_etap).apply()
        return user

    async def update_balance(self, user_id, tokens):
        user = await User.query.where(User.user_id == user_id).gino.first()
        new_balance = user.balance + tokens
        await user.update(balance=new_balance).apply()
        return user

    async def new_opponent(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        new_opponent = user.opponent + 1
        new_etap = 1
        await user.update(opponent=new_opponent, etap=new_etap).apply()
        return user

    async def new_game(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        new_game = user.game + 1
        new_opponent = 1
        new_etap = 1
        await user.update(game=new_game, opponent=new_opponent, etap=new_etap).apply()
        return user


POSTGRESURI = f'postgresql://local:local@0.0.0.0:5432/gino'


async def start_db():
    await db.set_bind(POSTGRESURI)


async def create_db():
    # POSTGRESURI = f'postgresql://local:local@0.0.0.0:5432/gino'
    await db.set_bind(POSTGRESURI)
    # await db.gino: GinoSchemaVisitor
    await db.gino.create_all()
    await db.pop_bind().close()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(create_db())
