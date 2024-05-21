import logging
import random

import datetime
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

from main import dp, bot, db, config, Tools
admin = config()['telegram']['admin']

"""
Обработка команды /waiter
"""


def waiter_action(first_name, location):
    print(f"│ [{Tools.timenow()}] {first_name} → {location}")

async def start(message: types.Message):
    user = message.from_user.id
    # Новый официант:
    if not db.check_waiter_exists(user):
        # Регистрируем официанта:
        db.add_waiter(
            user,
            f'tg://user?id={user}',
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
        text = f'\n🙋🏻‍♂️Новый официант:' \
               f'\n' \
               f'\n<b>{message.from_user.first_name} {message.from_user.last_name}</b>' \
               f'\n@{message.from_user.username}' \
               f'\nid <a href="tg://user?id={user}">{user}</a>' \
               f'\n'
        await bot.send_message(user, text)
    else:
        text = f'\nВы уже зарегистрировались как официант'
        await bot.send_message(user, text)


async def get_order(message: types.Message, order):
    user = message.from_user.id
    # Проверяем официанта:
    if db.check_waiter_exists(user):
        text = f'\nНовый заказ:' \
               f'\n' \
               f'\n<b>{order}</b>' \
               f'\n'
        await bot.send_message(user, text)


"""
Обработка команды /waiter
"""

