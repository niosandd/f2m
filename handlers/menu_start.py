import logging
import random

import datetime
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

from main import dp, bot, db, config, Tools
admin = config()['telegram']['admin']

"""
Обработка команды /start
"""


def user_action(first_name, location):
    print(f"│ [{Tools.timenow()}] {first_name} → {location}")

async def start(message: types.Message):
    user = message.from_user.id

    # Новый пользователь:
    if not db.check_users_user_exists(user):

        # Регистрируем пользователя:
        reg_time = Tools.timenow()
        db.add_users_user(
            user,
            f'tg://user?id={user}',
            reg_time,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
        text = f'\n🙋🏻‍♂️Новый посетитель:' \
               f'\n' \
               f'\n<b>{message.from_user.first_name} {message.from_user.last_name}</b>' \
               f'\n@{message.from_user.username}' \
               f'\nid <a href="tg://user?id={user}">{user}</a>' \
               f'\n' \
               f'\n<code>{reg_time}</code>'

        await bot.send_message(admin, text)
        db.set_users_mode(user, 0, 'start')

    # Данные чата:
    try:
        await bot.delete_message(user, call.message.message_id)
    except:
        pass
    first = int(db.get_users_first_message(user))
    last = int(db.get_users_last_message(user)) + 1
    db.set_users_first_message(user, 0)
    db.set_users_last_message(user, 0)

    # Действие:
    db.set_users_mode(user, 0, 'start')

    if db.check_client(user):
        message_obj = await bot.send_message(
            chat_id=user,
            text=f"<b>Привет!</b> 👋\n"
                    f"\n"
                    f"На связи ✨<b>food2mood</b>✨ - сервис персональных рекомендаций блюд под настроение! 😃🍽️\n\n"
                    f"<blockquote>«В каждом блюде содержится <i>множество веществ, витаминов и минералов</i>, которые по-разному воздействуют на нервную систему»🧑‍⚕️🩺</blockquote>\n\n"
                    f"Искусственный интеллект food2mood проанализирует их и составит подборку <b>специально для тебя!</b> ❤️\n\n"
                    f"🤝 <b>Мы помним тебя, друг!\n</b>"
                    f"Ты можешь получать рекомендации сразу или обновить информацию в анкете 📝\n"
                    f"\n",
            parse_mode='HTML',
            reply_markup=buttons_start_02()
        )
    else:
        message_obj = await bot.send_message(
            chat_id=user,
            text=f"<b>Привет!</b> 👋\n"
                    f"\n"
                    f"На связи <b>food2mood</b> - сервис персональных рекомендаций блюд под настроение 😃🍽️\n"
                    f"\n"
                    f"<blockquote>«В каждом блюде содержится множество веществ, витаминов и минералов, "
                 f"которые по-разному воздействуют на нервную систему» - 🧑‍⚕️🩺</blockquote>\n\n"
                    f"<b>food2mood</b> проанализирует их и <u>составит подборки блюд специально для тебя!</u>\n"
                    f"\n"
                    f"Чтобы начать, заполни анкету из 3 простых вопросов! 👇",
            parse_mode='HTML',
            reply_markup=buttons_start_01()
        )

    if int(db.get_users_first_message(user)) == 0:
        db.set_users_first_message(user, message_obj.message_id)
    db.set_users_last_message(user, message_obj.message_id)

    # Очистка чата:
    if int(db.get_users_first_message(user)) != 0:
        for i in range(first, last, 1):
            try:
                await bot.delete_message(user, int(i))
            except Exception as ex:
                pass

@dp.callback_query_handler(text_contains=f"menu_start")
async def menu_start(call: types.CallbackQuery):
    user = call.from_user.id
    db.set_users_mode(user, call.message.message_id, 'start')

    # Данные чата:
    try:
        await bot.delete_message(user, call.message.message_id)
    except:
        pass
    first = int(db.get_users_first_message(user))
    last = int(db.get_users_last_message(user)) + 1
    db.set_users_first_message(user, 0)
    db.set_users_last_message(user, 0)

    # Действие:
    db.set_users_mode(user, 0, 'start')

    if db.check_client(user):
        message_obj = await bot.send_message(
            chat_id=user,
            text=f"<b>Привет!</b>👋\n"
                    f"\n"
                    f"На связи ✨<b>food2mood</b>✨ - сервис персональных рекомендаций блюд под настроение! 😃🍽️\n\n"
                    f"<blockquote>«В каждом блюде содержится <i>множество веществ, витаминов и минералов</i>, которые по-разному воздействуют на нервную систему»🧑‍⚕️🩺</blockquote>\n\n"
                    f"Искусственный интеллект food2mood проанализирует их и составит подборку <b>специально для тебя!</b> ❤️\n\n"
                    f"🤝<b>Мы помним тебя, друг!\n</b>"
                    f"Ты можешь получать рекомендации сразу или обновить информацию в анкете 📝\n"
                    f"\n",
            reply_markup=buttons_start_02()
        )
    else:
        message_obj = await bot.send_message(
            chat_id=user,
            text=f"<b>Привет!</b> 👋\n"
                    f"\n"
                    f"На связи <b>food2mood</b> - сервис персональных рекомендаций блюд под настроение 😃🍽️\n"
                    f"\n"
                    f"<blockquote>«В каждом блюде содержится множество веществ, витаминов и минералов, "
                 f"которые по-разному воздействуют на нервную систему» - 🧑‍⚕️🩺</blockquote>\n\n"
                    f"<b>food2mood</b> проанализирует их и <u>составит подборки блюд специально для тебя!</u>\n"
                    f"\n"
                    f"Чтобы начать, заполни анкету из 3 простых вопросов! 👇",
            reply_markup=buttons_start_01()
        )



    if int(db.get_users_first_message(user)) == 0:
        db.set_users_first_message(user, message_obj.message_id)
    db.set_users_last_message(user, message_obj.message_id)

    # Очистка чата:
    if int(db.get_users_first_message(user)) != 0:
        for i in range(first, last, 1):
            try:
                await bot.delete_message(user, int(i))
            except Exception as ex:
                pass


def buttons_start_01():
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="ЗАПОЛНИТЬ АНКЕТУ 📋",
                                callback_data="client_register")

    menu.add(btn1)

    return menu



def buttons_start_02():
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="Получить рекомендации! 🍤",
                                callback_data="food_mood")

    btn2 = InlineKeyboardButton(text="Заполнить анкету заново 📋",
                                callback_data="client_register_again")

    btn3 = InlineKeyboardButton(text="Мои f2m коины 🪙",
                                callback_data="food_to_mood_coin_status")

    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)

    return menu

"""
Обработка команды /start
"""

