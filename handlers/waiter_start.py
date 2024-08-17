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


def ind_to_number(ind):
    numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    result = ""
    for char in str(ind):
        result += numbers[int(char)]
    return result


async def start(message: types.Message):
    user = message.from_user.id
    try:
        info = message.text.split("/")
        name = info[0].split()
        rest = info[1]
        # Новый официант:
        if not db.check_waiter_exists(user):
            # Регистрируем официанта:
            db.add_waiter(
                user,
                rest,
                f'tg://user?id={user}',
                message.from_user.username,
                name[0],
                name[1],
                name[2]
            )
            text = f'\n🙋🏻‍♂️Новый официант:' \
                   f'\n' \
                   f'\n<b>Ресторан {rest}</b>' \
                   f'\n<b>{name[0]} {name[1]} {name[2]}</b>' \
                   f'\n@{message.from_user.username}' \
                   f'\nid <a href="tg://user?id={user}">{user}</a>' \
                   f'\n'
            await bot.send_message(user, text)
        else:
            text = f'\nТы уже зарегистрировался(ась) как официант'
            await bot.send_message(user, text)
    except Exception:
        text = f'\nОшибка ввода ФИО/ресторан'
        await bot.send_message(user, text)


async def get_order(message: types.Message, order):
    user = message.from_user.id
    # Проверяем официанта:
    if db.check_waiter_exists(user):
        name = db.get_users_user_first_name(order) + " " + db.get_users_user_last_name(order)
        if not db.get_waiter_score(user):
            temp_list = [order]
        else:
            temp_list = eval(db.get_waiter_score(user))
            temp_list.append(order)
        db.set_waiter_score(user, str(temp_list))
        try:
            basket = list(eval(db.get_basket(order)).keys())
        except Exception as e:
            print("waiter error", e)
            basket = []
        order_text = ""
        for i in range(len(basket)):
            order_text += ind_to_number(i + 1) + " " + basket[i] + "\n"
        text = f'\n<b>Новый заказ:</b>' \
               f'\n\n' \
               f'{order_text}' \
               f'\n <b>Количество твоих уникальных заказов: {len(set(temp_list))}</b>'
        await bot.send_message(user, text)


"""
Обработка команды /waiter
"""
