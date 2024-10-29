import logging
import random

import datetime
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
import time
from main import dp, bot, db, config, Tools
admin = config()['telegram']['admin']

"""
Обработка команды /start
"""


async def start(message: types.Message):
    user = message.from_user.id

    # Новый пользователь:
    if not db.check_users_user_exists(user):

        # Регистрируем пользователя:
        reg_time = time.timenow()
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

    first = int(db.get_users_first_message(user))
    last = int(db.get_users_last_message(user)) + 1
    db.set_users_first_message(user, 0)
    db.set_users_last_message(user, 0)

    # Действие:
    db.set_users_mode(user, 0, 'start')


    message_obj = await bot.send_message(
        chat_id=user,
        text=f"<b>Привет!</b> 👋\n"
<<<<<<< Updated upstream
                f"\n"
                f"На связи ✨<b>food2mood</b>✨ - сервис персональных рекомендаций блюд под настроение! 😃🍽️\n\n"
                f"Нутрициолог и искусственный интеллект food2mood анализируют позиции меню и составляют подборку специально для тебя! ❤️\n\n"
                f"<b>Выбирай своё настроение! Мы начинаем! ⚡️\n\n</b>"
                f'<b>Команды в разделе "Меню:"</b>\n'
                f"<i>/start - запуск food2mood\n</i>"
                f"<i>/form - тест на выявление твоих вкусовых предпочтений\n</i>"
                f"<i>/f2m_coins - информация о нашей валюте, которую можно обменять на подарки от партнеров\n</i>"
                f"\n",
=======
             f"\n"
             f"На связи ✨<b>food2mood</b>✨ - нейросеть рекомендаций еды под настроение! 👾🍽️\n\n"
             f"Food2mood обучена на исследованиях специалистов по питанию. Она анализирует меню заведения и составляет подборки специально для тебя!❤️️\n\n"
             f"А еще food2mood умеет находить заведения под настроение🔍\n"
             f"<b>Нажимай кнопку «Выбрать настроение»! Мы начинаем! ⚡️\n\n</b>"
             f'<b>Команды в разделе "Меню:"</b>\n'
             f"<i>/start - запуск food2mood\n</i>"
             f"<i>/form - тест на выявление твоих вкусовых предпочтений\n</i>"
             f"<i>/f2m_coins - информация о нашей валюте, которую можно обменять на подарки от партнеров\n</i>"
             f"\n",
>>>>>>> Stashed changes
        parse_mode='HTML',
        reply_markup=buttons_start_02()
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

    try:
        sex = db.get_client_sex(user)
        age = db.get_client_age(user)
        style = db.get_client_style(user)
        blacklist = db.get_client_blacklist(user)
        if not (sex and sex != 'None'):
            db.set_client_sex(user, 'не определен 🤷')
        if not (age and age != 'None'):
            db.set_client_age(user, 'не определен 🤷')
        if not (style and style != 'None'):
            db.set_client_style(user, 'Стандартное')
        if not (blacklist and blacklist != 'None'):
            db.set_client_blacklist(user, 'Пусто')
    except Exception as e:
        print(e)

    message_obj = await bot.send_message(
        chat_id=user,
        text=f"<b>Привет!</b> 👋\n"
             f"\n"
<<<<<<< Updated upstream
             f"На связи ✨<b>food2mood</b>✨ - сервис персональных рекомендаций блюд под настроение! 😃🍽️\n\n"
             f"Нутрициолог и искусственный интеллект food2mood анализируют позиции меню и составляют подборку специально для тебя! ❤️\n\n"
             f"<b>Выбирай своё настроение! Мы начинаем! ⚡️\n\n</b>"
=======
             f"На связи ✨<b>food2mood</b>✨ - нейросеть рекомендаций еды под настроение! 👾🍽️\n\n"
             f"Food2mood обучена на исследованиях специалистов по питанию. Она анализирует меню заведения и составляет подборки специально для тебя!❤️️\n\n"
             f"А еще food2mood умеет находить заведения под настроение🔍\n"
             f"<b>Нажимай кнопку «Выбрать настроение»! Мы начинаем! ⚡️\n\n</b>"
>>>>>>> Stashed changes
             f'<b>Команды в разделе "Меню:"</b>\n'
             f"<i>/start - запуск food2mood\n</i>"
             f"<i>/form - тест на выявление твоих вкусовых предпочтений\n</i>"
             f"<i>/f2m_coins - информация о нашей валюте, которую можно обменять на подарки от партнеров\n</i>"
             f"\n",
        reply_markup=buttons_start_02()
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

    btn1 = InlineKeyboardButton(text="Выбрать настроение",
                                callback_data="food_mood")

    # btn2 = InlineKeyboardButton(text="Заполнить анкету заново 📋",
    #                             callback_data="client_register_again")
    #
    # btn3 = InlineKeyboardButton(text="Мои f2m коины 🪙",
    #                             callback_data="food_to_mood_coin_status")

    menu.add(btn1)
    # menu.add(btn2)
    # menu.add(btn3)

    return menu

"""
Обработка команды /start
"""

