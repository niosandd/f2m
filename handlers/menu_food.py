from __future__ import annotations
import random
import pandas as pd
import os
import time

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    ReplyKeyboardMarkup, InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InputMediaPhoto
from aiogram.utils.deep_linking import get_start_link

from main import dp, bot, db, config

from db import Database
import menu

import pyqrcode

admin = config()['telegram']['admin']
local_recommendation_text = ''
media = []
foods_photo_message_id = []
media_for_category = []
foods_photo_for_category_message_id = []

icons = {
    "Салаты и закуски": "🥗",
    "Первые блюда": "🍲",
    "Горячие блюда": "🍛",
    "Гарниры": "🍚",
    "Десерты": "🍰",
    "Напитки": "☕",
    "Завтрак": "🍳",
    "Ужин": "🍽️",
    "Японская кухня": "🍣",
    "Поке": "🥢",
    "Холодные закуски": "🧊",
    "Закуски": "😋",
    "Салаты": "🥗",
    "Супы": "🍲",
    "Паста": "🍝",
    "Горячие закуски": "🔥",
    "Хлеб": "🍞",
    "Соус": "🧉",
    "Дары моря": "🦞",
    "Мясо и птица": "🥩",
    "Радость": "🤩",
    "Печаль": "😢",
    "Гнев": "😡",
    "Спокойствие": "😌",
    "Волнение": "😬",
    "Нутрициолог": "👩🏻‍💻",
    "Пользователи": "🙋🏻‍♀️",
    "Обломов": "⭐",
    "Ивлев": "⭐",
    1: "🥇",
    2: "🥈",
    3: "🥉",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
    10: "🔟",
    11: "1️⃣1️⃣",
    12: "1️⃣2️⃣",
    13: "1️⃣3️⃣",
    14: "1️⃣4️⃣",
    15: "1️⃣5️⃣",
    16: "1️⃣6️⃣",
    17: "1️⃣7️⃣",
    18: "1️⃣8️⃣",
    19: "1️⃣9️⃣",
    20: "2️⃣0️⃣",
    21: "2️⃣1️⃣",
    22: "2️⃣2️⃣",
    23: "2️⃣3️⃣",
    24: "2️⃣4️⃣",
    25: "2️⃣5️⃣",
    26: "2️⃣6️⃣",
    27: "2️⃣7️⃣",
    28: "2️⃣8️⃣",
    29: "2️⃣9️⃣",
    30: "3️⃣0️⃣",
    31: "3️⃣1️⃣",
    32: "3️⃣2️⃣",
    33: "3️⃣3️⃣",
    34: "3️⃣4️⃣",
    35: "3️⃣5️⃣",
    36: "3️⃣6️⃣",
    37: "3️⃣7️⃣",
    38: "3️⃣8️⃣",
    39: "3️⃣9️⃣",
    40: "4️⃣0️⃣",
    41: "4️⃣1️⃣",
    42: "4️⃣2️⃣",
    43: "4️⃣3️⃣",
    44: "4️⃣4️⃣",
    45: "4️⃣5️⃣",
    46: "4️⃣6️⃣",
    47: "4️⃣7️⃣",
    48: "4️⃣8️⃣",
    49: "4️⃣9️⃣",
    50: "5️⃣0️⃣",
    'Галочка': "✅"
}

"""
Выбор настроения
"""


@dp.callback_query_handler(text_contains=f"food_mood")
async def food_mood(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')
    if db.get_users_ban(user):
        return None
    db.set_client_temp_mood(user, None)
    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"<b>Пожалуйста, выбери своё настроение👇</b>",
        reply_markup=buttons_food_00()
    )
    db.set_users_mode(user, message_obj.message_id, 'food_mood')


def buttons_food_00():
    menu = InlineKeyboardMarkup(row_width=3)

    btn1 = InlineKeyboardButton(text=f"Радость {icons['Радость']}",
                                callback_data="food_choose_get_Радость")

    btn2 = InlineKeyboardButton(text=f"Печаль {icons['Печаль']}",
                                callback_data="food_choose_get_Печаль")

    btn3 = InlineKeyboardButton(text=f"Гнев {icons['Гнев']}",
                                callback_data="food_choose_get_Гнев")

    btn4 = InlineKeyboardButton(text=f"Спокойствие {icons['Спокойствие']}",
                                callback_data="food_choose_get_Спокойствие")

    btn5 = InlineKeyboardButton(text=f"Волнение {icons['Волнение']}",
                                callback_data="food_choose_get_Волнение")

    btn9 = InlineKeyboardButton(text="« Назад",
                                callback_data="menu_start")

    menu.add(btn1, btn2, btn3)
    menu.add(btn4, btn5)
    menu.add(btn9)

    return menu


"""
Выбрать самому или по рекомендациям
"""

# @dp.callback_query_handler(text_contains=f"food_choose_get")
# async def food_choose_get(call: types.CallbackQuery):
#     user = call.from_user.id
#     data = call.data.split('_')
#     if db.get_users_ban(user):
#         return None
#
#         # Действие:
#     if len(data) > 2:
#         db.set_client_temp_mood(user, data[-1])
#
#     # db.set_client_temp_rest(user, None)  Зачем это вообще надо?
#     message_obj = await bot.edit_message_text(
#         chat_id=user,
#         message_id=call.message.message_id,
#         text=f"<b>Отлично! Мы учли твоё настроение!</b> 🤝\n\n"
#         # f"Не знаешь, куда сходить под выбранное настроение? Жми кнопку <b>«Куда сходить? 💫»</b>\n"
#         # f"<blockquote>Мы с удовольствием порекомендуем место, где тебе будет хорошо💆‍♂️💆‍♀️</blockquote>\n\n"
#              f"<i>Уже в заведении?</i> Если нет, мы поможем его подобрать! 🔍"
#              f"\n",
#         reply_markup=buttons_food_01()
#     )
#     db.set_users_mode(user, message_obj.message_id, 'food_choose_get')
flag = True


def get_user_profile_text(user_id):
    global flag
    # Извлекаем данные из базы данных с использованием соответствующих функций
    sex = db.get_client_sex(user_id)
    age = db.get_client_age(user_id)
    style = db.get_client_style(user_id)
    blacklist = db.get_client_blacklist(user_id)
    whitelist = db.get_client_whitelist(user_id)

    # Устанавливаем значения по умолчанию, если данных нет или они равны None

    try:
        flag = True
        if not (sex and sex != 'None'):
            sex = 'не определен 🤷'
            db.set_client_sex(user_id, 'не определен 🤷')
            flag = False
        if not (age and age != 'None'):
            age = 'не определен 🤷'
            db.set_client_age(user_id, 'не определен 🤷')
            flag = False
        if not (style and style != 'None') or style == 'Стандартное':
            style = 'Стандартный 🥘'
            db.set_client_style(user_id, 'Стандартное')
        if not (blacklist and blacklist != 'None') or blacklist == "Пусто":
            blacklist = 'пусто ⭕️'
            db.set_client_blacklist(user_id, 'Пусто')
            flag = False
        if not (whitelist and whitelist != 'None') or whitelist == "Пусто":
            whitelist = 'пусто ⭕️'
            flag = False
            db.set_client_whitelist(user_id, 'Пусто')
        if not (style and style != 'None'):
            flag = False
    except Exception as e:
        print(e)
    # Формируем текст сообщения
    if age == "18":
        age = "До 18"
    elif age == "25":
        age = "18-25"
    elif age == "35":
        age = "26-35"
    elif age == "45":
        age = "36-45"
    emojis = {
        "Мужчина": "🙋🏻‍♂",
        "Женщина": "🙋🏻‍♀",
        "Стандартное": "🥘",
        "Диетическое": "🥗",
        "Вегетарианство": "🧀",
        "Веганство": "🥜",
        "Сыроедение": "🥦"
    }
    if sex in emojis and style in emojis:
        message_text = (
            f"<b>Твоя анкета 📃</b>\n\n"
            f"<b>——— Пол ———</b>\n"
            f"{sex} {emojis[sex]}\n\n"
            f"<b>——— Возраст ———</b>\n"
            f"{age}\n\n"
            f"<b>——— Стиль питания ———</b>\n"
            f"{style} {emojis[style]}\n\n"
            f"<b>——— НЕ ЕШЬ ———</b>\n"
            f"{blacklist}\n\n"
            f"<b>——— ПРЕДПОЧИТАЕШЬ ———</b>\n"
            f"{whitelist}"
        )
    else:
        message_text = (
            f"<b>Твоя анкета 📃</b>\n\n"
            f"<b>——— Пол ———</b>\n"
            f"{sex}\n\n"
            f"<b>——— Возраст ———</b>\n"
            f"{age}\n\n"
            f"<b>——— Стиль питания ———</b>\n"
            f"{style}\n\n"
            f"<b>——— НЕ ЕШЬ ———</b>\n"
            f"{blacklist}\n\n"
            f"<b>——— ПРЕДПОЧИТАЕШЬ ———</b>\n"
            f"{whitelist}"
        )
    return message_text


@dp.callback_query_handler(text_contains=f"food_choose_get")
async def food_choose_get(call: types.CallbackQuery):
    global flag
    user = call.from_user.id
    data = call.data.split('_')
    if db.get_users_ban(user):
        return None
    message_text = get_user_profile_text(user)
    if '+' in call.data:
        message_text = ('✨ Теперь давай выберем место под <b>твоё настроение!</b> \n\n'
                        '⚡ <b>Нажимай "Получить рекомендацию"</b>, чтобы мы посоветовали тебе заведение под настроение! \n\n'
                        '🔎 Если ты <b>уже знаешь куда идти, нажимай "Список заведений"</b> и ищи нужное место \n\n'
                        '📷 Если ты <b>уже в заведении, наведи камеру телефона на QR</b> твоего места')

        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=message_text,
            reply_markup=buttons_food_001()
        )
        db.set_users_mode(user, message_obj.message_id, 'food_inline_handler_y')
    else:
        if not flag:
            if len(data) > 3:
                db.set_client_temp_mood(user, data[-1])

            last_qr_time = db.get_client_last_qr_time(user)
            if (round(time.time()) - last_qr_time) // 3600 <= 3:

                message_obj = await bot.edit_message_text(
                    chat_id=user,
                    message_id=call.message.message_id,
                    text=message_text,
                    reply_markup=buttons_food_01()
                )
                db.set_users_mode(user, message_obj.message_id, 'food_choose_get')
            else:

                message_text = ('✨ Теперь давай выберем место под <b>твоё настроение!</b> \n\n'
                                '⚡ <b>Нажимай "Получить рекомендацию"</b>, чтобы мы посоветовали тебе заведение под настроение! \n\n'
                                '🔎 Если ты <b>уже знаешь куда идти, нажимай "Список заведений"</b> и ищи нужное место \n\n'
                                '📷 Если ты <b>уже в заведении, наведи камеру телефона на QR</b> твоего места')

                message_obj = await bot.edit_message_text(
                    chat_id=user,
                    message_id=call.message.message_id,
                    text=message_text,
                    reply_markup=buttons_food_001()
                )
                db.set_users_mode(user, message_obj.message_id, 'food_inline_handler_y')
        else:
            if len(data) > 3:
                db.set_client_temp_mood(user, data[-1])
            message_text = ('✨ Теперь давай выберем место под <b>твоё настроение!</b> \n\n'
                            '⚡ <b>Нажимай "Получить рекомендацию"</b>, чтобы мы посоветовали тебе заведение под настроение! \n\n'
                            '🔎 Если ты <b>уже знаешь куда идти, нажимай "Список заведений"</b> и ищи нужное место \n\n'
                            '📷 Если ты <b>уже в заведении, наведи камеру телефона на QR</b> твоего места')

            message_obj = await bot.edit_message_text(
                chat_id=user,
                message_id=call.message.message_id,
                text=message_text,
                reply_markup=buttons_food_001()
            )
            db.set_users_mode(user, message_obj.message_id, 'food_inline_handler_y')


def buttons_food_001():
    menu = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="Получить рекомендацию", callback_data="rest_recommendation")
    btn2 = InlineKeyboardButton(text="Список заведений 🔍", switch_inline_query_current_chat='')
    btn9 = InlineKeyboardButton(text="« Поменять настроение",
                                callback_data="food_mood")
    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn9)

    return menu


@dp.message_handler(commands=['form'])
async def send_profile(message: types.Message):
    user = message.from_user.id
    message_text = get_user_profile_text(user)
    await message.answer(text=message_text, reply_markup=buttons_food_01())


def buttons_food_01():
    menu = InlineKeyboardMarkup(row_width=3)

    btn1 = InlineKeyboardButton(text="Все так! ✅", callback_data="confirmation_of_the_questionnaire")
    btn2 = InlineKeyboardButton(text="Изменить анкету 📝", callback_data="client_register_again")
    btn3 = InlineKeyboardButton(text="« Назад", callback_data="food_mood")
    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)
    return menu


"""
Выбор ресторана
"""


@dp.callback_query_handler(text_contains=f"food_restaurant")
async def food_restaurant(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')
    if db.get_users_ban(user):
        return None

    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"<b>Выбери заведение в поиске, чтобы посмотреть меню👇🏻\n</b>",
        reply_markup=buttons_food_02()
    )
    db.set_users_mode(user, message_obj.message_id, 'food_inline_handler')


def buttons_food_02():
    menu = InlineKeyboardMarkup(row_width=3)

    btn1 = InlineKeyboardButton(text="🔎 Поиск кафе", switch_inline_query_current_chat='')
    btn9 = InlineKeyboardButton(text="« Поменять настроение",
                                callback_data="food_mood")
    menu.add(btn1)
    menu.add(btn9)

    return menu


@dp.callback_query_handler(lambda call: call.data == "confirmation_of_the_questionnaire")
async def confirmation_of_the_questionnaire(call: types.CallbackQuery):
    global media
    media = []
    user = call.from_user.id
    message_text = ('✨ Теперь давай выберем место под <b>твоё настроение!</b> \n\n'
                    '⚡ <b>Нажимай "Получить рекомендацию"</b>, чтобы мы посоветовали тебе заведение под настроение! \n\n'
                    '🔎 Если ты <b>уже знаешь куда идти, нажимай "Список заведений"</b> и ищи нужное место \n\n'
                    '📷 Если ты <b>уже в заведении, наведи камеру телефона на QR</b> твоего места')
    try:
        temp = db.get_client_temp_rest(user).split(':')
        temp_state = db.get_client_temp_mood(user)
        if not temp_state or temp_state == "None":
            db.set_client_temp_mood(user, "Радость")
        if len(temp) <= 1:
            db.set_users_mode(user, call.message.message_id, 'food_inline_handler_y')
            await bot.edit_message_text(
                chat_id=user,
                message_id=call.message.message_id,
                text=message_text,
                reply_markup=get_back())
        else:
            await food_rec2(user, "food_rec_Нутрициолог".split('_'))
    except Exception as e:
        print(e)


def get_back():
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="Получить рекомендацию", callback_data="rest_recommendation")
    btn2 = InlineKeyboardButton(text="Список заведений 🔍", switch_inline_query_current_chat='')

    btn = InlineKeyboardButton(text="« Вернуться назад", callback_data="food_choose_get")

    keyboard.add(btn1, btn2, btn)
    return keyboard


@dp.callback_query_handler(text_contains=f"rest_recommendation")
async def rest_recommendation(call: types.CallbackQuery):
    user = call.from_user.id
    db.set_users_mode(user, call.message.message_id, 'food_inline_handler_y')
    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text="Пока этот раздел в разработке. Выбери заведение из общего списка)",
        reply_markup=InlineKeyboardMarkup().row(
            InlineKeyboardButton(text="Список заведений 🔍", switch_inline_query_current_chat=''))
    )


token = ""

user_data = {}


async def search_and_select_restaurant(user_id, query):
    posts = db.restaurants_find_all(query.capitalize()) if len(query) > 0 else db.restaurants_get_all()

    if not posts:
        await bot.send_message(user_id, "Ресторана в базе нет 😔", reply_markup=qr_scanned_keyboard_none())

    else:
        first_restaurant = posts[0]
        rest_name = first_restaurant[1]
        rest_address = first_restaurant[2]
        # Установка данных о ресторане
        await dp.storage.set_data(user=user_id, data={'rest_name': rest_name, 'rest_address': rest_address})

        # Извлечение установленных данных
        user_data = await dp.storage.get_data(user=user_id)
        await bot.send_message(user_id,
                               f"🤔📍 Ты находишься в кафе <b>«{first_restaurant[1]}»</b>, по адресу: {first_restaurant[2]}?",
                               reply_markup=qr_scanned_keyboard())


def qr_scanned_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    choose_category_button = InlineKeyboardButton(text=f'Да, я здесь!', callback_data=f'apply_')
    change_restaurant_button = InlineKeyboardButton(text="Отсканировать заново", callback_data="scan_qrcode")
    change_mood_button = InlineKeyboardButton(text="« Вернуться назад", callback_data="scan_qrcode")
    keyboard.row(choose_category_button)
    keyboard.row(change_restaurant_button)
    keyboard.row(change_mood_button)
    return keyboard


def qr_scanned():
    keyboard = InlineKeyboardMarkup(row_width=3)
    choose_category_button = InlineKeyboardButton(text=f'Да, я здесь!', callback_data=f'food_rec_Нутрициолог')
    change_mood_button = InlineKeyboardButton(text="« Вернуться назад", callback_data="food_choose_get")
    keyboard.row(choose_category_button)
    keyboard.row(change_mood_button)
    return keyboard


def qr_scanned_keyboard_none():
    keyboard = InlineKeyboardMarkup(row_width=3)
    # change_restaurant_button = InlineKeyboardButton(text="Отсканировать заново", callback_data="scan_qrcode")
    change_mood_button = InlineKeyboardButton(text="« Вернуться назад", callback_data="scan_qrcode")
    keyboard.add(change_mood_button)
    return keyboard


"""
Выбор рекомендаций
"""


async def food_rec_get(user, message):
    mode = db.get_users_mode(user)
    data = message.text.split(':')

    # Действие:
    db.set_client_temp_rest(user, f"{data[0]}:{data[1]}")
    db.set_client_temp_recommendation(user, None)
    if db.check_basket_exists(user):
        db.set_basket(user, "{}")

    rest = db.get_client_temp_rest(user).split(':')
    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=mode['id'],
        text=f"Выбери, чьи рекомендации хочешь получить👇",
        reply_markup=buttons_food_03(rest[0])
    )
    db.set_users_mode(user, message_obj.message_id, 'food_rec')


@dp.callback_query_handler(text_contains=f"apply_")
async def food_rec_get3(call: types.CallbackQuery):
    user = call.from_user.id
    mode = db.get_users_mode(user)

    user_data = await dp.storage.get_data(user=user)
    # await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id) Более не актуально

    rest_name = user_data.get('rest_name')
    rest_address = user_data.get('rest_address')

    db.set_client_temp_rest(user, f"{rest_name}:{rest_address}")
    db.set_client_temp_recommendation(user, None)
    if db.check_basket_exists(user):
        db.set_basket(user, "{}")

    rest = db.get_client_temp_rest(user).split(':')
    message_obj = await bot.edit_message_text(
        chat_id=user,
        # message_id=mode['id'],
        message_id=call.message.message_id,
        text=f"Выбери, чьи рекомендации хочешь получить 👇🏻",
        reply_markup=buttons_food_03(rest[0])
    )
    db.set_users_mode(user, message_obj.message_id, 'food_rec')


@dp.callback_query_handler(text_contains=f"food_rec_get2")
async def food_rec_get2(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')
    if db.get_users_ban(user):
        return None

    # Действие:
    db.set_client_temp_recommendation(user, None)

    rest = db.get_client_temp_rest(user).split(':')
    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"Выбери, чьи рекомендации хочешь получить 👇🏻",
        reply_markup=buttons_food_03(rest[0])
    )
    db.set_users_mode(user, message_obj.message_id, 'food_rec_get2')


def buttons_food_03(rest: str):
    menu = InlineKeyboardMarkup(row_width=2)

    if db.restaurants_get_dish_rec_nutritionist(rest):
        btn1 = InlineKeyboardButton(text=f"👨‍⚕️ Нутрициолог",
                                    callback_data="food_rec_Нутрициолог")
        menu.row(btn1)

    if db.restaurants_get_dish_rec_community(rest):
        btn2 = InlineKeyboardButton(text=f" 🙋🏻‍♀ Пользователи",
                                    callback_data="food_rec_Пользователи")
        menu.row(btn2)

    if db.restaurants_get_dish_rec_a_oblomov(rest):
        btn3 = InlineKeyboardButton(text=f"⭐ Обломов",
                                    callback_data="food_rec_Обломов")
        menu.row(btn3)

    if db.restaurants_get_dish_rec_a_ivlev(rest):
        btn4 = InlineKeyboardButton(text=f"⭐ Ивлев",
                                    callback_data="food_rec_Ивлев")
        menu.row(btn4)

    btn9 = InlineKeyboardButton(text="« Поменять кафе",
                                callback_data="food_restaurant")
    menu.add(btn9)

    return menu


"""
Выбор категории блюд
"""


@dp.callback_query_handler(text_contains=f"back_to_categories")
async def back_to_categories(call: types.CallbackQuery):
    user = call.from_user.id

    rest_name = db.get_client_temp_rest(user).split(':')[0]
    available_categories = db.restaurants_get_all_categories(rest_name)
    if db.get_users_ban(user):
        return None
    db.set_client_temp_category(user, None)

    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"<b>Выбери категорию блюд из основного меню 🔍</b>\n\n"
             f"<i>PS: о сезонных предложениях тебе подробно расскажет официант\n</i>",
        reply_markup=buttons_food_04(available_categories)
    )
    db.set_users_mode(user, message_obj.message_id, 'food_rec')


@dp.callback_query_handler(text_contains='return_to_recommendation')
async def return_to_recommendation(call: types.CallbackQuery):
    global local_recommendation_text, media, foods_photo_message_id
    user = call.from_user.id
    openf = []
    photo_dir = 'Фудтумуд'
    all_files = {os.path.splitext(file)[0]: os.path.join(photo_dir, file) for file in os.listdir(photo_dir)}
    for e in media:
        file_path = all_files[e['caption'][7:]]
        photo = open(file_path, 'rb')
        openf.append(InputMediaPhoto(photo, caption=f"Блюдо: {e['caption'][7:]}"))
    # foods_photo_message_id = await bot.send_media_group(chat_id=user, media=openf)
    await bot.send_message(
        chat_id=user,
        text=local_recommendation_text,
        reply_markup=menu_button())

    await bot.delete_message(chat_id=user, message_id=call.message.message_id)


def generate_recommendation(user):
    db.add_user_action(user, 'Пользователь получил меню с рекомендацией')
    mood = db.get_client_temp_mood(user)
    style = db.get_client_style(user)
    restaurant = db.get_client_temp_rest(user).split(":")[0]
    blacklist = [ingredient.strip() for ingredient in db.get_client_blacklist(user).split(",")]
    # Загружаем таблицу с меню
    df = pd.DataFrame(db.restaurants_get(restaurant), columns=[
        'id',
        'Название ресторана',
        'Адрес ресторана',
        'Категория',
        'Название блюда',
        'Описание блюда',
        'Ингредиенты',
        'Стиль питания',
        'Настроение',
        'Рекомендации нутрициолога',
        'Рекомендации сообщества',
        'Рекомендации Обломова',
        'Ивлев',
        'Отзывы',
        'Рейтинг',
        'Коины',
        'Ссылка',
        'Цена',
        'Граммы',
        'Простые ингредиенты'
    ])

    df = df[df['Название ресторана'].str.contains(restaurant)]
    df = df[df['Настроение'].str.contains(mood)]
    df = df[df['Стиль питания'].str.contains(style)]
    if df.empty:
        return None
    dishes = []
    for dish in df.values.tolist():
        dish_ingredients = [ingredient.strip() for ingredient in str(dish[19]).lower().split(',')]
        if set(blacklist) & set(dish_ingredients):
            continue

        dishes.append({
            "Ресторан": dish[1],
            "Адрес": dish[2],
            "Категория": dish[3],
            "Название": dish[4],
        })
    if dishes:
        recommendation = []
        banned_categories = ["Хлеб", "Соус"]
        banned_dishes = []
        for _ in range(10):
            dish = random.choice(dishes)
            if dish['Название'] not in banned_dishes and dish["Категория"] not in banned_categories:
                recommendation.append((f"{dish['Категория']} {icons[dish['Категория']]}", dish["Название"]))
                banned_categories.append(dish["Категория"])
                banned_dishes.append(dish["Название"])
            if len(recommendation) == 5:
                break
        return recommendation
    else:
        return None


@dp.callback_query_handler(text_contains=f"food_rec")
async def food_rec(call: types.CallbackQuery):
    global local_recommendation_text, media, foods_photo_message_id
    user = call.from_user.id
    data = call.data.split('_')
    rest_name = db.get_client_temp_rest(user).split(':')[0]
    list_of_dishes = []
    if db.get_users_ban(user):
        return None
    db.set_client_temp_category(user, None)
    if len(data) > 2:
        db.set_client_temp_recommendation(user, data[-1])
    recommendation_text = f"<b>🥇 ТОП блюд кафе {rest_name} из разных категорий под твоё настроение:</b>\n\n"
    try:
        recommendation = generate_recommendation(user)
        db.set_client_recommendation(user, f"{recommendation}")
        rest = db.get_client_temp_rest(user)
        for dish in recommendation:
            list_with_info = (db.restaurants_get_dish(rest.split(':')[0], rest.split(':')[1], dish[1]))
            recommendation_text += f"<b>——{dish[0]}——</b>\n<i>{dish[1]}</i>\n\n"
            recommendation_text += f"💰 <i>Цена: {list_with_info[-3]} руб.</i>\n"
            recommendation_text += f"⚖️ <i>Вес: {list_with_info[-2]} г.</i>"

            recommendation_text += f"\n\n"
            list_of_dishes.append(dish[1])
        photo_dir = 'Фудтумуд'
        all_files = {os.path.splitext(file)[0]: os.path.join(photo_dir, file) for file in os.listdir(photo_dir)}
        open_files = []

        for index, dish_name in enumerate(list_of_dishes):
            if dish_name in all_files:
                file_path = all_files[dish_name]
                if os.path.isfile(file_path):
                    photo = open(file_path, 'rb')
                    open_files.append(photo)
                    media.append(InputMediaPhoto(photo, caption=f"Блюдо: {dish_name}"))

        if media:
            foods_photo_message_id = await bot.send_media_group(chat_id=user, media=media)
            for photo in open_files:
                photo.close()
            await bot.send_message(chat_id=user, text=local_recommendation_text, reply_markup=menu_button())
        else:
            await bot.send_message(chat_id=user, text="Фотографии не найдены.")
        db.set_client_rec_message_id(user, call.message.message_id)

    except Exception as e:
        print(e)


async def food_rec2(user, data):
    global local_recommendation_text, foods_photo_message_id, media
    mode = db.get_users_mode(user)
    rest_name = db.get_client_temp_rest(user).split(':')[0]
    list_of_dishes = []

    if db.get_users_ban(user):
        return None
    db.set_client_temp_category(user, None)
    if len(data) > 2:
        db.set_client_temp_recommendation(user, data[-1])
    recommendation_text = f"<b>🥇 ТОП блюд кафе {rest_name} из разных категорий под твоё настроение:</b>\n\n"
    try:
        recommendation = generate_recommendation(user)
        db.set_client_recommendation(user, f"{recommendation}")
        rest = db.get_client_temp_rest(user)
        for dish in recommendation:
            list_with_info = (db.restaurants_get_dish(rest.split(':')[0], rest.split(':')[1], dish[1]))
            recommendation_text += f"<b>——{dish[0]}——</b>\n<i>{dish[1]}</i>\n\n"
            recommendation_text += f"💰 <i>Цена: {list_with_info[-3]} руб.</i>\n"
            recommendation_text += f"⚖️ <i>Вес: {list_with_info[-2]} г.</i>"

            recommendation_text += f"\n\n"
            list_of_dishes.append(dish[1])
        photo_dir = 'Фудтумуд'
        all_files = {os.path.splitext(file)[0]: os.path.join(photo_dir, file) for file in os.listdir(photo_dir)}
        open_files = []

        for index, dish_name in enumerate(list_of_dishes):
            if dish_name in all_files:
                file_path = all_files[dish_name]
                if os.path.isfile(file_path):
                    photo = open(file_path, 'rb')
                    open_files.append(photo)
                    media.append(InputMediaPhoto(photo, caption=f"Блюдо: {dish_name}"))

        recommendation_text += "<b>Чтобы узнать о блюдах больше, посмотреть другие категории и сделать заказ, нажимай Меню 👇</b>"
        local_recommendation_text = recommendation_text
        db.set_client_rec_message_id(user, mode['id'])

        try:
            # if rest_name != "Блан де Блан":
            # if media:
            # foods_photo_message_id = await bot.send_media_group(chat_id=user, media=media)
            await bot.delete_message(chat_id=user, message_id=mode['id'])
            # for photo in open_files:
            # photo.close()

            # time.sleep(1)
            # message_obj = await bot.send_message(
            # chat_id=user,
            # message_id=mode['id'],
            # text=recommendation_text,
            # reply_markup=menu_button())
            message_obj = await bot.send_message(
                chat_id=user,
                text=recommendation_text,
                reply_markup=menu_button()
            )
        except:
            message_obj = await bot.send_message(
                chat_id=user,
                text=recommendation_text,
                reply_markup=menu_button()
            )

        db.set_users_mode(user, message_obj.message_id, 'food_rec')

    except Exception as e:
        print(e)


def menu_button():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text="Меню", callback_data="show_categories"))
    markup.add(InlineKeyboardButton(text="« Вернуться назад", callback_data="food_choose_get+"))
    return markup


@dp.callback_query_handler(text_contains=f"show_categories")
async def show_categories(call: types.CallbackQuery):
    global foods_photo_message_id, foods_photo_for_category_message_id
    try:
        user = call.from_user.id
        mode = db.get_users_mode(user)
        rest_name = db.get_client_temp_rest(user).split(':')[0]
        available_categories = db.restaurants_get_all_categories(rest_name)
        if db.get_users_ban(user):
            return None

        if "again" in call.data:
            await bot.delete_message(chat_id=user, message_id=mode['id'])
            message_obj = await bot.send_message(
                chat_id=user,
                text=f"<b>Выбери категорию блюд из основного меню 🔍</b>\n\n"
                     f"<i>PS: о сезонных предложениях тебе подробно расскажет официант\n</i>",
                reply_markup=buttons_food_04(available_categories)
            )

        else:
            # for mes in foods_photo_message_id:
            # await bot.delete_message(chat_id=user, message_id=mes["message_id"])
            message_obj = await bot.edit_message_text(chat_id=user, message_id=call.message.message_id,
                                                      text=f"<b>Выбери категорию блюд из основного меню 🔍</b>\n\n"
                                                           f"<i>PS: о сезонных предложениях тебе подробно расскажет официант\n</i>",
                                                      reply_markup=buttons_food_04(available_categories)
                                                      )
        foods_photo_message_id = []
        db.set_users_mode(user, message_obj.message_id, 'food_rec')
    except Exception as e:
        print(e)


def buttons_food_04(available_categories):
    menu = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text=f"Завтрак {icons['Завтрак']}",
                             callback_data="food_category_Завтрак") if "Завтрак" in available_categories else None,
        InlineKeyboardButton(text=f"Салаты/Закуски {icons['Салаты и закуски']}",
                             callback_data="food_category_Салаты и закуски") if "Салаты и закуски" in available_categories else None,
        InlineKeyboardButton(text=f"Салаты {icons['Салаты']}",
                             callback_data="food_category_Салаты") if "Салаты" in available_categories else None,
        InlineKeyboardButton(text=f"Горячие закуски {icons['Горячие закуски']}",
                             callback_data="food_category_Горячие закуски") if "Горячие закуски" in available_categories else None,
        InlineKeyboardButton(text=f"Закуски {icons['Закуски']}",
                             callback_data="food_category_Закуски") if "Закуски" in available_categories else None,
        InlineKeyboardButton(text=f"Горячие блюда {icons['Горячие блюда']}",
                             callback_data="food_category_Горячие блюда") if "Горячие блюда" in available_categories else None,
        InlineKeyboardButton(text=f"Супы {icons['Супы']}",
                             callback_data="food_category_Супы") if "Супы" in available_categories else None,
        InlineKeyboardButton(text=f"Холодные закуски {icons['Холодные закуски']}",
                             callback_data="food_category_Холодные закуски") if "Холодные закуски" in available_categories else None,
        InlineKeyboardButton(text=f"Мясо и птица {icons['Мясо и птица']}",
                             callback_data="food_category_Мясо и птица") if "Мясо и птица" in available_categories else None,
        InlineKeyboardButton(text=f"Паста {icons['Паста']}",
                             callback_data="food_category_Паста") if "Паста" in available_categories else None,
        InlineKeyboardButton(text=f"Дары моря {icons['Дары моря']}",
                             callback_data="food_category_Дары моря") if "Дары моря" in available_categories else None,
        InlineKeyboardButton(text=f"Гарниры {icons['Гарниры']}",
                             callback_data="food_category_Гарниры") if "Гарниры" in available_categories else None,
        InlineKeyboardButton(text=f"Японская кухня {icons['Японская кухня']}",
                             callback_data="food_category_Японская кухня") if "Японская кухня" in available_categories else None,
        InlineKeyboardButton(text=f"Поке {icons['Поке']}",
                             callback_data="food_category_Поке") if "Поке" in available_categories else None,
        InlineKeyboardButton(text=f"Десерты {icons['Десерты']}",
                             callback_data="food_category_Десерты") if "Десерты" in available_categories else None,
        InlineKeyboardButton(text=f"Напитки {icons['Напитки']}",
                             callback_data="food_category_Напитки") if "Напитки" in available_categories else None,
        # InlineKeyboardButton(text=f"Хлеб {icons['Хлеб']}",
        #                      callback_data="food_category_Хлеб") if "Хлеб" in available_categories else None,
        # InlineKeyboardButton(text="« Поменять автора рекомендаций", callback_data="food_rec_get2")
        InlineKeyboardButton(text="«Назад", callback_data="return_to_recommendation")
    ]

    # Фильтрация None значений из списка кнопок и добавление их в меню
    for button in filter(None, buttons):
        if button.callback_data != "food_rec_get2":  # Проверка, чтобы кнопки не располагались в одной строке с последней кнопкой
            menu.insert(button)
        else:
            menu.add(button)

    return menu


"""
Рекомендуем блюда
"""


@dp.callback_query_handler(text_contains=f"food_category")
async def food_category(call: types.CallbackQuery):
    global foods_photo_for_category_message_id
    try:
        user = call.from_user.id
        data = call.data.split('_')
        if db.get_users_ban(user):
            return None

        loading_message = await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=f"Одну секунду... ⏳"
        )
        category = '_'.join(data[2:])  # Если предполагается, что название категории может содержать подчеркивания
        if category:  # Проверка на наличие категории
            db.set_client_temp_category(user, category)

        rest = db.get_client_temp_rest(user).split(':')
        db.set_client_temp_dish(user, 0)
        dish, length, numb = menu.get_dish(user)
        if dish is not None:
            # ingredients = ""
            # for ing in dish['Ингредиенты']:
            #     ingredients += f"• {str(ing).strip()}\n"
            if dish['Ресторан'] == "Блан де Блан":
                text = (  # f"🍤 <b>Кафе:</b>\n"
                    # f"<i>«{dish['Ресторан']}», {dish['Адрес']}</i>\n"
                    # f"\n"
                    f"—— {icons[dish['Категория']]} <b>{dish['Категория']}</b> ——\n"
                    f"\n"
                    f"{icons[length - numb]} <i>{dish['Название']}</i>\n\n"
                    f"💰 <i>Цена: {dish['Цена']} руб.</i>\n"
                    f"⚖️ <i>Вес: {str(dish['Грамм'])} г.</i>"
                    f"\n\n"
                    # f"🧾 <b>Ингредиенты:</b>\n"
                    # f"<code>{ingredients}</code>\n"
                    f"—— {icons[dish['Настроение']]} <b>{dish['Настроение']}</b> ——\n"
                    f"\n"
                    f"<i>Узнай больше, нажав команду:</i>"
                    f"\n"
                    f"\n"
                    f"🔢/kbzhu - КБЖУ блюда"
                    f"\n"
                    f"🤖/com - Объяснение рекомендации от нейросети"
                    f"\n"
                    f"🧾/sostav - Состав блюда"
                    f"\n"
                    f"\n"
                    f"<i>Листай рекомендации с помощью кнопок « и »👇🏻</i>\n\n"
                    f"<b>Понравилось блюдо? Добавь его в корзину! 🛒</b>")
            else:
                text = (  # f"🍤 <b>Кафе:</b>\n"
                    # f"<i>«{dish['Ресторан']}», {dish['Адрес']}</i>\n"
                    # f"\n"
                    f"—— {icons[dish['Категория']]} <b>{dish['Категория']}</b> ——\n"
                    f"\n"
                    f"{icons[length - numb]} <i>{dish['Название']}</i>\n\n"
                    f"💰 <i>Цена: {dish['Цена']} руб.</i>\n"
                    f"⚖️ <i>Вес: {str(dish['Грамм'])} г.</i>"
                    f"\n\n"
                    # f"🧾 <b>Ингредиенты:</b>\n"
                    # f"<code>{ingredients}</code>\n"
                    f"—— {icons[dish['Настроение']]} <b>{dish['Настроение']}</b> ——\n"
                    f"\n"
                    f"<i>Узнай больше, нажав команду:</i>"
                    f"\n"
                    f"\n"
                    f"🔢/kbzhu - КБЖУ блюда"
                    f"\n"
                    f"🤖/com - Объяснение рекомендации от нейросети"
                    f"\n"
                    f"🧾/sostav - Состав блюда"
                    f"\n"
                    f"\n"
                    f"<i>Листай рекомендации с помощью кнопок « и »👇🏻</i>\n\n"
                    f"<b>Понравилось блюдо? Добавь его в корзину! 🛒</b>")
            if db.check_basket_exists(user):
                basket = eval(db.get_basket(user))
                if dish['Название'] in basket:
                    in_basket = True
                else:
                    in_basket = False
            else:
                in_basket = False
            photo_dir = 'Фудтумуд'
            all_files = {os.path.splitext(file)[0]: os.path.join(photo_dir, file) for file in os.listdir(photo_dir)}
            if dish['Название'] in all_files and dish['Ресторан'] == 'Молодёжь':
                file_path = all_files[dish['Название']]
                if os.path.isfile(file_path):
                    await bot.delete_message(
                        chat_id=user,
                        message_id=loading_message.message_id,
                    )
                    message_obj = await bot.send_photo(user, open(file_path, 'rb'),
                                                       caption=text,
                                                       reply_markup=buttons_food_05(
                                                           db.get_client_temp_dish(user),
                                                           length, numb, in_basket))
                    foods_photo_for_category_message_id = message_obj
                else:
                    message_obj = await bot.edit_message_text(
                        chat_id=user,
                        message_id=loading_message.message_id,
                        text=text,

                        reply_markup=buttons_food_05(db.get_client_temp_dish(user), length, numb, in_basket)
                    )
                    foods_photo_for_category_message_id = message_obj
            else:
                message_obj = await bot.edit_message_text(
                    chat_id=user,
                    message_id=loading_message.message_id,
                    text=text,

                    reply_markup=buttons_food_05(db.get_client_temp_dish(user), length, numb, in_basket)
                )
            foods_photo_for_category_message_id = message_obj
            db.set_client_can_alert(user, round(time.time()))
            db.set_client_temp_dish_id(user, db.restaurants_get_dish(rest[0], rest[1], dish['Название'])[0])
        else:
            message_obj = await bot.edit_message_text(
                chat_id=user,
                message_id=loading_message.message_id,
                text=f"🍤 <b>Кафе:</b>\n"
                     f"<i>«{rest[0]}», {rest[1]}</i>\n"
                     f"\n"
                     f"——— {icons[db.get_client_temp_category(user)]} <b>{db.get_client_temp_category(user)}</b> ———\n"
                     f"\n"
                     f"<b>Кажется, в этом заведении нет блюд, подходящих под ваши критерии</b> 🤔\n"
                     f"\n"
                     f"Попробуй поменять категорию блюд, настроение или список продуктов, которые ты не употребляешь в пищу 😉\n"

                     f"——— {icons[db.get_client_temp_mood(user)]} <b>{db.get_client_temp_mood(user)}</b> ———\n",
                reply_markup=buttons_food_05(None, None, None, None)
            )
            foods_photo_for_category_message_id = message_obj
        db.set_users_mode(user, message_obj.message_id, 'food_category')
    except Exception as e:
        print("category error", e)


@dp.callback_query_handler(text_contains=f"send_dish")
async def send_dish(call: types.CallbackQuery):
    global foods_photo_for_category_message_id
    try:
        user = call.from_user.id
        mode = db.get_users_mode(user)
        data = call.data.split('_')
        if db.get_users_ban(user):
            return None

        if "del" in data[-1]:
            try:
                message_id = call.data.split("send_dish_del")[-1]
                await bot.delete_message(user, int(message_id))
            except TypeError:
                pass
            except Exception as e:
                print(e)

        # Действие:

        if data[-1] == 'next':
            db.set_client_temp_dish(user, db.get_client_temp_dish(user) + 1)
        elif data[-1] == 'back':
            db.set_client_temp_dish(user, db.get_client_temp_dish(user) - 1)

        rest = db.get_client_temp_rest(user).split(':')
        dish, length, numb = menu.get_dish(user)

        # ingredients = ""
        # for ing in dish['Ингредиенты']:
        #     ingredients += f"• {str(ing).strip()}\n"
        if dish['Ресторан'] == "Блан де Блан":
            text = (  # f"🍤 <b>Кафе:</b>\n"
                # f"<i>«{dish['Ресторан']}», {dish['Адрес']}</i>\n"
                # f"\n"
                f"—— {icons[dish['Категория']]} <b>{dish['Категория']}</b> ——\n"
                f"\n"
                f"{icons[length - numb]} <i>{dish['Название']}</i>\n\n"
                f"💰 <i>Цена: {dish['Цена']} руб.</i>\n"
                f"⚖️ <i>Вес: {str(dish['Грамм'])} г.</i>"
                f"\n\n"
                # f"🧾 <b>Ингредиенты:</b>\n"
                # f"<code>{ingredients}</code>\n"
                f"—— {icons[dish['Настроение']]} <b>{dish['Настроение']}</b> ——\n"
                f"\n"
                f"<i>Узнай больше, нажав команду:</i>"
                f"\n"
                f"\n"
                f"🔢/kbzhu - КБЖУ блюда"
                f"\n"
                f"🤖/com - Объяснение рекомендации от нейросети"
                f"\n"
                f"🧾/sostav - Состав блюда"
                f"\n"
                f"\n"
                f"<i>Листай рекомендации с помощью кнопок « и »👇🏻</i>\n\n"
                f"<b>Понравилось блюдо? Добавь его в корзину! 🛒</b>")
        else:
            text = (  # f"🍤 <b>Кафе:</b>\n"
                # f"<i>«{dish['Ресторан']}», {dish['Адрес']}</i>\n"
                # f"\n"
                f"—— {icons[dish['Категория']]} <b>{dish['Категория']}</b> ——\n"
                f"\n"
                f"{icons[length - numb]} <i>{dish['Название']}</i>\n\n"
                f"💰 <i>Цена: {dish['Цена']} руб.</i>\n"
                f"⚖️ <i>Вес: {str(dish['Грамм'])} г.</i>"
                f"\n\n"
                # f"🧾 <b>Ингредиенты:</b>\n"
                # f"<code>{ingredients}</code>\n"
                f"—— {icons[dish['Настроение']]} <b>{dish['Настроение']}</b> ——\n"
                f"\n"
                f"<i>Узнай больше, нажав команду:</i>"
                f"\n"
                f"\n"
                f"🔢/kbzhu - КБЖУ блюда"
                f"\n"
                f"🤖/com - Объяснение рекомендации от нейросети"
                f"\n"
                f"🧾/sostav - Состав блюда"
                f"\n"
                f"\n"
                f"<i>Листай рекомендации с помощью кнопок « и »👇🏻</i>\n\n"
                f"<b>Понравилось блюдо? Добавь его в корзину! 🛒</b>")
        if db.check_basket_exists(user):
            basket = eval(db.get_basket(user))
            if dish['Название'] in basket:
                in_basket = True
            else:
                in_basket = False
        else:
            in_basket = False
        message_obj = None
        if dish['Ресторан'] == "Молодёжь":
            photo_dir = 'Фудтумуд'
            all_files = {os.path.splitext(file)[0]: os.path.join(photo_dir, file) for file in os.listdir(photo_dir)}
            message_obj = None
            last_message = foods_photo_for_category_message_id
            if 'photo' in last_message:
                if dish['Название'] in all_files:
                    file_path = all_files[dish['Название']]
                    f = open(file_path, 'rb')
                    try:
                        photo = InputMediaPhoto(media=f, caption=text)
                        if os.path.isfile(file_path):
                            message_obj = await bot.edit_message_media(chat_id=user,
                                                                       message_id=call.message.message_id,
                                                                       media=photo,
                                                                       reply_markup=buttons_food_05(
                                                                           db.get_client_temp_dish(
                                                                               user),
                                                                           length, numb,
                                                                           in_basket))

                            foods_photo_for_category_message_id = message_obj
                    finally:
                        f.close()
                else:
                    await bot.delete_message(chat_id=user, message_id=call.message.message_id)
                    message_obj = await bot.send_message(
                        chat_id=user,
                        text=text,
                        reply_markup=buttons_food_05(db.get_client_temp_dish(user), length, numb, in_basket)
                    )
                    foods_photo_for_category_message_id = message_obj
            else:
                if dish['Название'] in all_files:
                    file_path = all_files[dish['Название']]
                    f = open(file_path, 'rb')
                    try:
                        if os.path.isfile(file_path):
                            await bot.delete_message(chat_id=user, message_id=mode['id'])
                            message_obj = await bot.send_photo(user, f, caption=text, reply_markup=buttons_food_05(
                                db.get_client_temp_dish(
                                    user),
                                length, numb,
                                in_basket))
                            foods_photo_for_category_message_id = message_obj
                    finally:
                        f.close()
                else:
                    message_obj = await bot.edit_message_text(
                        chat_id=user,
                        message_id=call.message.message_id,
                        text=text,
                        reply_markup=buttons_food_05(db.get_client_temp_dish(user), length, numb, in_basket)
                    )
                    foods_photo_for_category_message_id = message_obj

        else:
            message_obj = await bot.edit_message_text(
                chat_id=user,
                message_id=call.message.message_id,
                text=text,
                reply_markup=buttons_food_05(db.get_client_temp_dish(user), length, numb, in_basket)
            )
            foods_photo_for_category_message_id = message_obj
        db.set_users_mode(user, message_obj.message_id, 'send_dish')
        db.set_client_can_alert(user, round(time.time()))
        db.set_client_temp_dish_id(user, db.restaurants_get_dish(rest[0], rest[1], dish['Название'])[0])
    except Exception as e:
        print(e)


def calc_basket_cost(user):
    summary = 0
    if db.check_basket_exists(user):
        basket = eval(db.get_basket(user))
        for dish in basket:
            summary += int(db.get_dish_price(basket[dish])[0][0])
    return summary


@dp.callback_query_handler(text_contains=f"check_order")
async def check_order(call: types.CallbackQuery):
    global foods_photo_for_category_message_id
    try:
        user = call.from_user.id
        mode = db.get_users_mode(user)
        basket_cost = calc_basket_cost(user)
        text = "❗️<b>Проверь корзину, перед тем как сделать заказ</b> ❗️\n\n" \
               "<i><b>Нажми на позицию</b>, чтобы убрать ее из корзины 🚫\n" \
               "<b>Вернись к категориям</b>, чтобы добавить еще блюда ➕</i>\n\n" \
               f"<i><b>🛒ИТОГО</b>: {basket_cost} руб.</i>"
        if 'photo' not in foods_photo_for_category_message_id:
            message_obj = await bot.edit_message_text(
                chat_id=user,
                message_id=call.message.message_id,
                text=text,
                reply_markup=generate_basket(user)
            )
        else:
            await bot.delete_message(chat_id=user, message_id=mode['id'])
            message_obj = await bot.send_message(chat_id=user, text=text, reply_markup=generate_basket(user))
        foods_photo_for_category_message_id = []
        db.set_users_mode(user, message_obj.message_id, 'check_order')
    except Exception as e:
        print("order error", e)


@dp.callback_query_handler(text_contains=f"create_qr")
async def create_qr(call: types.CallbackQuery):
    user = call.from_user.id

    # Удаление предыдущего сообщения
    await call.message.delete()

    url = await get_start_link(f"or{user}", encode=True)
    qrcode = pyqrcode.create(url)
    qrcode.png('QR CODE.png', scale=5)
    with open('QR CODE.png', 'rb') as file:
        msg = await bot.send_photo(user, photo=file)
    await bot.send_message(user,
                           text="Покажи этот QR-код <b>официанту</b>, чтобы он принял заказ 📥\n\n",
                           reply_markup=create_qr_keyboard(msg["message_id"]),
                           parse_mode='HTML')


@dp.callback_query_handler(text_contains=f"basket")
async def change_basket(call: types.CallbackQuery):
    try:
        user = call.from_user.id
        if not db.check_basket_exists(user):
            db.create_basket(user)
        basket_mode = call.data.split("basket_")[-1]
        dish, length, numb = menu.get_dish(user)
        dish_id = db.get_client_temp_dish_id(user)
        dish = db.restaurants_get_by_id(dish_id)[4]
        basket = eval(db.get_basket(user))
        if basket_mode == "add":
            basket[dish] = dish_id
            in_basket = True
        else:
            try:
                basket.pop(dish, None)
            except ValueError:
                pass
            in_basket = False
        db.set_basket(user, str(basket))
        await bot.edit_message_reply_markup(
            chat_id=user,
            message_id=call.message.message_id,
            reply_markup=buttons_food_05(db.get_client_temp_dish(user), length, numb, in_basket))
    except Exception as e:
        print("basket error", e)


@dp.callback_query_handler(text_contains=f"delete")
async def change_basket(call: types.CallbackQuery):
    try:
        user = call.from_user.id
        dish_id = call.data.split("delete_")[-1]
        dish = db.restaurants_get_by_id(dish_id)[4]
        basket = eval(db.get_basket(user))
        try:
            basket.pop(dish, None)
        except ValueError:
            pass
        db.set_basket(user, str(basket))
        basket_cost = calc_basket_cost(user)
        text = "❗️<b>Проверь корзину, перед тем как сделать заказ</b> ❗️\n\n" \
               "<i><b>Нажми на позицию</b>, чтобы убрать ее из корзины 🚫\n" \
               "<b>Вернись к категориям</b>, чтобы добавить еще блюда ➕</i>\n\n" \
               f"<i><b>🛒ИТОГО</b>: {basket_cost} руб.</i>"
        await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=text,
            reply_markup=generate_basket(user))
    except Exception as e:
        print("basket error", e)


@dp.callback_query_handler(text_contains=f"bon_appetite")
async def bon_appetite(call: types.CallbackQuery):
    user = call.from_user.id
    mode = db.get_users_mode(user)['id']
    message_id = call.data.split("bon_appetite")[-1]
    try:
        await bot.delete_message(user, int(message_id))
    except Exception as e:
        print(e)
    try:
        await bot.delete_message(user, db.get_client_rec_message_id(user))
    except Exception as e:
        print(e)
    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"<b>Спасибо, что воспользовался сервисом <a href='https://t.me/food_2_mood'>food2mood</a>!❤️</b>\n\n"
             f"<i>Приятного аппетита!</i>",
        reply_markup=bon_appetite_keyboard(),
        parse_mode='HTML'
    )
    db.add_users_order(user, db.get_client_temp_rest(user), db.get_basket(user))
    db.set_basket(user, "{}")
    db.set_client_can_alert(user, 0)
    db.set_users_mode(user, mode, 'write_review')
    await asyncio.sleep(10)  # Подождать час
    try:
        await bot.delete_message(chat_id=user, message_id=message_obj.message_id)
    except:
        pass
    await send_reminder_message(user)  # Отправить напоминалку


async def send_reminder_message(user_id):
    user_first_name = db.get_users_user_first_name(user_id)
    cafe = db.get_last_users_order(user_id)[-1].split(':')[0]
    keyboard = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="Оставить отзыв", callback_data="leave_a_review")
    btn2 = InlineKeyboardButton(text="Не интересно", callback_data="menu_start")
    keyboard.add(btn1, btn2)

    await bot.send_message(
        chat_id=user_id,
        text=f"<b>{user_first_name}</b>, хочешь проконсультироваться по вопросам питания у нашего нутрициолога <strike>5000 руб/час</strike> совершенно бесплатно? 🤫🆓\n\nТогда оставь отзыв о кафе <b>{cafe}</b>!\n\nЗа эту активность мы начислим тебе f2m коины 🪙\n\n"
             f"Накопив определенное количество f2m коинов, ты сможешь обменять их на консультацию у нашего нутрициолога 🧑‍⚕️🩺🥙",
        reply_markup=keyboard
    )


def bon_appetite_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="«« Вернуться на главную",
                                callback_data="menu_start")

    btn2 = InlineKeyboardButton(text="« Вернуться к категориям",
                                callback_data="back_to_categories")

    btn3 = InlineKeyboardButton(text="« Вернуться к рекомендациям", callback_data="return_to_recommendation")

    keyboard.row(btn1)
    keyboard.row(btn2)
    keyboard.row(btn3)
    return keyboard


def create_qr_keyboard(message_id):
    keyboard = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="Готово!",
                                callback_data=f"bon_appetite{message_id}")

    btn2 = InlineKeyboardButton(text="« Вернуться к рекомендациям",
                                callback_data=f"send_dish_del{message_id}")

    keyboard.row(btn1)
    keyboard.row(btn2)
    return keyboard


def generate_basket(user):
    try:
        if db.check_basket_exists(user):
            basket = eval(db.get_basket(user))
        else:
            basket = {}
        keyboard = InlineKeyboardMarkup(row_width=1)
        if len(basket) > 0:
            for dish in basket:
                btn = InlineKeyboardButton(text=icons['Галочка'] + ' ' + str(dish),
                                           callback_data=f"delete_{basket[dish]}")
                keyboard.row(btn)
            btn1 = InlineKeyboardButton(text="« Вернуться к рекомендациям", callback_data="send_dish")
            btn2 = InlineKeyboardButton(text="Оформить заказ ‼️",
                                        callback_data="create_qr")
            keyboard.row(btn1)
            keyboard.row(btn2)
        else:
            btn0 = InlineKeyboardButton(text="« Ваша корзина пуста", callback_data="send_dish")
            keyboard.row(btn0)
        return keyboard
    except Exception as e:
        print("generate error", e)


import asyncio
from aiogram import types


@dp.callback_query_handler(text_contains="leave_a_review")
async def leave_a_review_global(call: types.CallbackQuery):
    user = call.from_user.id
    mode = db.get_users_mode(user)['id']

    # Удаление предыдущего сообщения
    await call.message.delete()

    # Отправка нового сообщения с клавиатурой
    message = await bot.send_message(
        chat_id=user,
        text="Найдите блюдо в поиске 🔎",
        reply_markup=search_dish_keyboard()
    )

    db.set_client_can_alert(user, 0)
    db.set_users_mode(user, mode, 'write_review')

    # Запуск задачи по удалению сообщения через 5 секунд
    await schedule_message_deletion(message)


async def schedule_message_deletion(message):
    await asyncio.sleep(10)  # Задержка в 5 секунд
    await message.delete()


def search_dish_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)

    search_activate_button = InlineKeyboardButton(text="Поиск блюд 🔍", switch_inline_query_current_chat='')
    keyboard.add(search_activate_button)

    return keyboard


def buttons_food_05(dish: int | None, length: int | None, last: int | None, in_basket: bool | None = None):
    menu = InlineKeyboardMarkup(row_width=3)
    if dish is not None:
        if length != 1:
            if dish > 0:
                btn1 = InlineKeyboardButton(text=f"« {length - last - 1}",
                                            callback_data="send_dish_back")

                if last == 0:
                    menu.row(btn1)
                else:
                    btn2 = InlineKeyboardButton(text=f"{length - last + 1} »",
                                                callback_data="send_dish_next")
                    menu.row(btn1, btn2)
            else:
                btn2 = InlineKeyboardButton(text=f"{length - last + 1} »",
                                            callback_data="send_dish_next")
                menu.add(btn2)
        if in_basket:
            btn0 = InlineKeyboardButton(text="Убрать из 🛒",
                                        callback_data=f"basket_remove")
        else:
            btn0 = InlineKeyboardButton(text="Добавить в 🛒",
                                        callback_data=f"basket_add")
        menu.add(btn0)
    # menu_start
    btn1 = InlineKeyboardButton(text="« Вернуться к категориям",
                                callback_data="show_categories_again")

    # btn2 = InlineKeyboardButton(text="«« Вернуться на главную",
    #                             callback_data="menu_start")

    btn3 = InlineKeyboardButton(text="Сделать заказ ❗️", callback_data="check_order")
    menu.add(btn1)
    # menu.add(btn2)
    menu.add(btn3)
    return menu


"""
Промокод
"""
#
# import string
#
#
# def generate_promo_code():
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
#
#
# @dp.callback_query_handler(lambda c: c.data == '12345')
# async def process_callback_12345(callback_query: types.CallbackQuery):
#     user_id = callback_query.from_user.id
#
#     user_reg_time_str = db.get_users_user_reg_time(user_id)
#     user_reg_time = datetime.datetime.strptime(user_reg_time_str, "%Y-%m-%d %H:%M:%S")
#     current_datetime = datetime.datetime.now()
#
#     if user_reg_time.date() == current_datetime.date():
#         promo_code = generate_promo_code()
#         message_text = (
#             f"Ваш промокод: {promo_code}\n"
#             "\n"
#             "Скажите это своему официанту и получите скидку 5% на весь заказ!"
#         )
#         await bot.send_message(callback_query.from_user.id, message_text)
#
#     else:
#         await bot.send_message(callback_query.from_user.id,
#                                "Извините, промокод доступен только для новых пользователей.")


"""
Рекомендуем блюда
"""


@dp.callback_query_handler(text_contains=f"food_choose_random")
async def food_choose_random(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')
    if db.get_users_ban(user):
        return None

    # Действие:
    dish, len_dish = menu.get_recommendation(user)

    if dish is not None:
        # ingredients = ""
        # for ing in dish['Ингредиенты'].split(','):
        #     ingredients += f"• {str(ing).strip()}\n"

        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=f"Учитывая твоё настроение, мы рекомендуем посетить 😌👇🏻\n"
                 f"\n"
                 f"🍤 <b>Кафе:</b>\n"
                 f"<i>«{dish['Ресторан']}», {dish['Адрес']}</i>\n"
                 f'<a href="{dish["Ссылка"]}">➡️ Узнать всё меню заведения</a>'
                 f"\n"
                 f"И попробовать там ☺️🌸\n"
                 f"\n"
                 f"——— {icons[dish['Категория']]} <b>{dish['Категория']}</b> ———\n"
                 f"\n"
                 f"💫 <i>«{dish['Название']}»</i>\n"
                 f"\n"
            # f"🧾 <b>Ингредиенты:</b>\n"
            # f"<code>{ingredients}</code>\n"
                 f"——— {icons[dish['Настроение']]} <b>{dish['Настроение']}</b> ———\n"
                 f"\n"
                 f"🗣️: <i>{dish['Описание']}</i> \n"
                 f"\n",
            reply_markup=buttons_food_06(True, len_dish)
        )
        db.set_client_can_alert(user, round(time.time()))
        db.set_client_temp_dish_id(user, db.restaurants_get_dish(dish['Ресторан'], dish['Адрес'], dish['Название'])[0])
        db.set_users_mode(user, message_obj.message_id,
                          'food_choose_random')
    else:
        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=f"<b>На сегодня у нас закончились все рекомендации</b> 💫\n",
            reply_markup=buttons_food_06(False, 0)
        )
        db.set_users_mode(user, message_obj.message_id, 'food_choose_random')


def buttons_food_06(full: bool = True, len_dish: int = 0):
    menu = InlineKeyboardMarkup(row_width=3)

    if full and len_dish > 1:
        btn1 = InlineKeyboardButton(text="Поменять рекомендацию 💫",
                                    callback_data="food_choose_random")
        menu.add(btn1)

    btn2 = InlineKeyboardButton(text="« Вернуться назад",
                                callback_data="food_choose_get")

    btn3 = InlineKeyboardButton(text="«« Вернуться на главную",
                                callback_data="menu_start")
    menu.add(btn2)
    menu.add(btn3)

    return menu
