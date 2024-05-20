import asyncio
import logging
import random
import telebot
import os

import aiohttp
from PIL import Image
from pyzbar.pyzbar import decode
from io import BytesIO
import requests

import datetime
import time
import sqlite3

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    ReplyKeyboardMarkup, InlineQuery, InputTextMessageContent, InlineQueryResultArticle

import qr_for_waiter
from main import dp, bot, db, config, Tools

from db import Database
import menu

token = "7016628811:AAEsbZR29HQ6GPmMS3aamYFduUsaXoPT1Ew"
admin = config()['telegram']['admin']
telepuzik =telebot.TeleBot(token)

icons = {
    "Салаты и закуски": "🥗",
    "Первые блюда": "🍲",
    "Горячие блюда": "🍛",
    "Гарниры": "🍚",
    "Десерты": "🍰",
    "Напитки": "☕",
    "Завтрак": "🧑🏻‍🍳",
    "Ужин": "🍽️",
    "Японская кухня": "🍣",
    "Поке": "🥢",
    "Холодные закуски": "😋🧊",
    "Салаты": "🥗",
    "Супы": "🍲",
    "Паста": "🍝",
    "Горячие закуски": "😋🔥",
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
    50: "5️⃣0️⃣"
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

    # Действие:
    db.set_client_temp_mood(user, None)
    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"Пожалуйста, выбери своё текущее настроение, чтобы мы порекомендовали блюда специально для тебя! 👇🏻",
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


@dp.callback_query_handler(text_contains=f"food_choose_get")
async def food_choose_get(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')
    if db.get_users_ban(user):
        return None

        # Действие:
    if len(data) > 2:
        db.set_client_temp_mood(user, data[-1])

    db.set_client_temp_rest(user, None)
    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"<b>Отлично! Мы учли твоё настроение!</b> 🤝\n\n"
             f"Не знаешь, куда сходить под выбранное настроение? Жми кнопку <b>«Куда сходить? 💫»</b>\n"
            f"<blockquote>Мы с удовольствием порекомендуем место, где тебе будет хорошо💆‍♂️💆‍♀️</blockquote>\n\n"
             f"➡️ Если ты уже находишься в заведении - жми <b>«Уже в заведении»</b>"
             f"\n",
        reply_markup=buttons_food_01()
    )
    db.set_users_mode(user, message_obj.message_id, 'food_choose_get')


def buttons_food_01():
    menu = InlineKeyboardMarkup(row_width=3)

    btn1 = InlineKeyboardButton(text="Выбрать заведение 🍤", callback_data="food_restaurant")
    btn3 = InlineKeyboardButton(text="Уже в заведении 📸", callback_data="scan_qrcode")
    btn2 = InlineKeyboardButton(text="Куда сходить? 💫", callback_data="food_choose_random")
    btn9 = InlineKeyboardButton(text="« Поменять настроение", callback_data="food_mood")
    # menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)
    menu.add(btn9)

    return menu


# def buttons_food_01():
#     menu = InlineKeyboardMarkup(row_width=3)
#
#     btn1 = InlineKeyboardButton(text="Выбрать заведение 🍤", callback_data="food_restaurant")
#     btn3 = InlineKeyboardButton(text="📸 Отсканировать QR-код", callback_data="scan_qrcode")
#     btn2 = InlineKeyboardButton(text="Куда сходить? 💫", callback_data="food_choose_random")
#     btn9 = InlineKeyboardButton(text="« Поменять настроение", callback_data="food_mood")
#     menu.add(btn1)
#     menu.add(btn2)
#     menu.add(btn3)
#     menu.add(btn9)
#
#     return menu


"""
Выбор ресторана
"""


@dp.callback_query_handler(text_contains=f"food_restaurant")
async def food_restaurant(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')
    if db.get_users_ban(user):
        return None

    # Действие:
    db.set_client_temp_rest(user, None)

    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"Пожалуйста, выберите в 🔎 <b>поиске</b> ваше любимое кафе, "
             f"и мы с удовольствием подберём для вас меню этого заведения 👇🏻\n"
             f"\n"
             f"Готовы посоветовать что-то вкусненькое! 😉",
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



@dp.callback_query_handler(lambda call: call.data == "scan_qrcode")
async def request_qr_photo(call: types.CallbackQuery):
    user = call.from_user.id

    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text="🔍 Друг, скорей <b>фотографируй</b> QR-код своего заведения <b>и присылай</b> его нам в чат! \n\n"
             "Ты найдешь его на оборотной стороне буклета с "
             "QR-кодом самого сервиса food2mood непосредственно в заведении🔖 \n\nОсталось всего лишь:"
             "<blockquote>📎->🤳-> 📸 -> 🔖-> 📤</blockquote>",
        reply_markup=get_back())


def get_back():
    keyboard = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="« Вернуться назад",
                                callback_data="food_choose_get")

    keyboard.add(btn1)
    return keyboard

token = "7016628811:AAEsbZR29HQ6GPmMS3aamYFduUsaXoPT1Ew"


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message: types.Message):

    user_id = message.from_user.id
    try:
        # Получение информации о файле асинхронно
        file_info = await bot.get_file(message.photo[-1].file_id)
        file_path = f'https://api.telegram.org/file/bot{token}/{file_info.file_path}'

        # Загрузка файла с использованием requests (синхронно)
        file = requests.get(file_path)
        image = Image.open(BytesIO(file.content))

        # Декодирование QR-кода
        qr_result = decode(image)
        if qr_result:
            decoded_data = qr_result[0].data.decode()
            # Используйте текст из QR как поисковой запрос
            search_query = decoded_data.split('/')[-1]  # или какой-то другой способ получения текста для поиска
            await search_and_select_restaurant(user_id, search_query)
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        else:
            await bot.send_message(user_id, "QR-код не распознан. Попробуйте еще раз.", reply_markup=qr_scanned_keyboard_none())
    except Exception as e:
        await bot.reply_to(message, str(e))
    finally:
        # Удаление сообщения с фотографией QR-кода после обработки
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

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
        await bot.send_message(user_id, f"🤔📍 Ты находишься в кафе <b>«{first_restaurant[1]}»</b>, по адресу: {first_restaurant[2]}?",
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


def qr_scanned_keyboard_none():
    keyboard = InlineKeyboardMarkup(row_width=3)
    change_restaurant_button = InlineKeyboardButton(text="Отсканировать заново", callback_data="scan_qrcode")
    change_mood_button = InlineKeyboardButton(text="« Вернуться назад", callback_data="scan_qrcode")
    keyboard.add(change_restaurant_button, change_mood_button)
    return keyboard


# def qr_scanned_keyboard(rest_name):
#     keyboard = InlineKeyboardMarkup(row_width=3)
#     choose_category_button = InlineKeyboardButton(text="Да, я нахожусь в этом ресторане",
#                                                   switch_inline_query_current_chat=f'{rest_name}')
#
#     change_restaurant_button = InlineKeyboardButton(text="Отсканировать заново", callback_data="scan_qrcode")
#     change_mood_button = InlineKeyboardButton(text="« Поменять настроение", callback_data="food_mood")
#     keyboard.add(choose_category_button, change_restaurant_button, change_mood_button)
#     return keyboard
# def qr_scanned_keyboard(rest_name):
#     keyboard = InlineKeyboardMarkup(row_width=3)
#     choose_category_button = InlineKeyboardButton(text=f'Да, я нахожусь в этом ресторане', callback_data=f'apply_{rest_name}')
#     change_restaurant_button = InlineKeyboardButton(text="Отсканировать заново", callback_data="scan_qrcode")
#     change_mood_button = InlineKeyboardButton(text="« Поменять настроение", callback_data="food_mood")
#     keyboard.add(choose_category_button, change_restaurant_button, change_mood_button)
#     return keyboard
#
# def qr_scanned_keyboard_none():
#     keyboard = InlineKeyboardMarkup(row_width=3)
#     change_restaurant_button = InlineKeyboardButton(text="Отсканировать заново", callback_data="scan_qrcode")
#     change_mood_button = InlineKeyboardButton(text="« Поменять настроение", callback_data="food_mood")
#     keyboard.add(change_restaurant_button, change_mood_button)
#     return keyboard


"""
Выбор рекомендаций
"""


async def food_rec_get(user, message):
    mode = db.get_users_mode(user)
    data = message.text.split(':')

    # Действие:
    db.set_client_temp_rest(user, f"{data[0]}:{data[1]}")
    db.set_client_temp_recommendation(user, None)

    rest = db.get_client_temp_rest(user).split(':')
    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=mode['id'],
        text=f"Выберите, кто будет рекомендовать вам блюда 👇🏻",
        reply_markup=buttons_food_03(rest[0])
    )
    db.set_users_mode(user, message_obj.message_id, 'food_rec')

# @dp.callback_query_handler(text_contains=f"apply_restaurant")
# async def food_rec_get3(call: types.CallbackQuery):
#     user = call.from_user.id
#     dp.send_message(call.from_user.id, "Вы подтвердили своё нахождение в ресторане")
#
#     db.set_users_mode(user, call.message_obj.message_id, 'apply_restaurant')

#КЛАСССС

# @dp.callback_query_handler(lambda c: c.data == 'apply_restaurant_confirmed')
# async def restaurant_confirmation(call: types.CallbackQuery):
#     # Эмулируем получение сообщения от пользователя
#     user_id = call.from_user.id
#     # Обработка "сообщения" от пользователя, как будто он отправил "Привет, Бот"
#     await process_user_message(user_id, 'Привет, Бот')
#     # Подтверждение получения команды пользователем, если нужно
#     await call.answer("Ваше присутствие в ресторане подтверждено.", show_alert=True)
#
# async def process_user_message(user_id: int, message_text: str):
#     # Логика обработки сообщения пользователя, например:
#     print(f"Получено сообщение от {user_id}: {message_text}")
#     # Отправка ответа или выполнение действия в зависимости от сообщения
#     # Здесь может быть любая логика, например, отправка подтверждения или информации обратно пользователю
#     await bot.send_message(chat_id=user_id, text=f"Вы сказали: {message_text}")

# @dp.inline_handler(lambda c: c.data and c.data.startswith('apply_restaurant_confirmed'))
# async def inline_echo(inline_query: InlineQuery):
#     user_id = inline_query.from_user.id
#     # Специальный вариант для отправки "ПРИВЕТ БОТ" от пользователя
#     result = InlineQueryResultArticle(
#         id='unique_id',  # Уникальный идентификатор результата
#         title="Сказать 'ПРИВЕТ БОТ'",
#         input_message_content=InputTextMessageContent("ПРИВЕТ БОТ")
#     )
#     # Отправка результата пользователю
#     await inline_query.answer([result], cache_time=1)

# @dp.callback_query_handler(text_contains=f"apply_")
# async def food_rec_get3(call: types.CallbackQuery):
#     user = call.from_user.id
#     _, rest_name = call.data.split('_')
#     await bot.send_message(call.from_user.id, f"соси {rest_name}")
#     # await food_rec_get_inside(user, call.message)

@dp.callback_query_handler(text_contains=f"apply_")
async def food_rec_get3(call: types.CallbackQuery):
    user = call.from_user.id
    mode = db.get_users_mode(user)

    user_data = await dp.storage.get_data(user=user)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    rest_name = user_data.get('rest_name')
    rest_address = user_data.get('rest_address')

    db.set_client_temp_rest(user, f"{rest_name}:{rest_address}")
    db.set_client_temp_recommendation(user, None)

    rest = db.get_client_temp_rest(user).split(':')
    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=mode['id'],
        text=f"Выберите, кто будет рекомендовать вам блюда 👇🏻",
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
        text=f"Выберите, кто будет рекомендовать вам блюда 👇🏻",
        reply_markup=buttons_food_03(rest[0])
    )
    db.set_users_mode(user, message_obj.message_id, 'food_rec_get2')

def buttons_food_03(rest: str):
    menu = InlineKeyboardMarkup(row_width=2)

    if db.restaurants_get_dish_rec_nutritionist(rest):
        btn1 = InlineKeyboardButton(text=f"👩🏻‍💻 Нутрициолог",
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

        # Действие:
    db.set_client_temp_category(user, None)

    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"Выберите категорию блюд 👇🏻\n",
        reply_markup=buttons_food_04(available_categories)
    )
    db.set_users_mode(user, message_obj.message_id, 'food_rec')


@dp.callback_query_handler(text_contains=f"food_rec")
async def food_rec(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')

    rest_name = db.get_client_temp_rest(user).split(':')[0]
    available_categories = db.restaurants_get_all_categories(rest_name)
    if db.get_users_ban(user):
        return None

    # Отправка стикера
    sticker_message = await bot.send_sticker(
        chat_id=user,
        sticker='CAACAgIAAxkBAAEFcOlmRG4AAaLHIqgW8CtAOWHhGN6y4XgAAkRYAAJCaghK0Zngs-8IqK81BA'
    )
    await asyncio.sleep(3)
    await bot.delete_message(chat_id=user, message_id=sticker_message.message_id)

    # Действие:
    db.set_client_temp_category(user, None)
    if len(data) > 2:
        db.set_client_temp_recommendation(user, data[-1])

    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"Выберите категорию блюд 👇🏻\n",
        reply_markup=buttons_food_04(available_categories)
    )
    db.set_users_mode(user, message_obj.message_id, 'food_rec')


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
        InlineKeyboardButton(text=f"Хлеб {icons['Хлеб']}",
                             callback_data="food_category_Хлеб") if "Хлеб" in available_categories else None,
        InlineKeyboardButton(text="« Поменять автора рекомендаций", callback_data="food_rec_get2")
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
    user = call.from_user.id

    data = call.data.split('_')
    if db.get_users_ban(user):
        return None

        # Действие:
    category = '_'.join(data[2:])  # Если предполагается, что название категории может содержать подчеркивания
    if category:  # Проверка на наличие категории
        db.set_client_temp_category(user, category)

    rest = db.get_client_temp_rest(user).split(':')
    db.set_client_temp_dish(user, 0)
    dish, length, numb = menu.get_dish(user)

    if dish is not None:
        ingredients = ""
        for ing in dish['Ингредиенты']:
            ingredients += f"• {str(ing).strip()}\n"
        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=f"🍤 <b>Кафе:</b>\n"
                 f"<i>«{dish['Ресторан']}», {dish['Адрес']}</i>\n"
                 f"\n"
                 f"—— {icons[dish['Категория']]} <b>{dish['Категория']}</b> ——\n"
                 f"\n"
                 f"{icons[length - numb]} <i>«{dish['Название']}»</i>\n"
                 f"\n"
                 # f"🧾 <b>Ингредиенты:</b>\n"
                 # f"<code>{ingredients}</code>\n"
                 f"—— {icons[dish['Настроение']]} <b>{dish['Настроение']}</b> ——\n"
                 f"\n"
                 f"🗣️: <i>{dish['Описание']}</i>\n"
                 f"\n"
                 f"<i>Листайте блюда кнопками '«' и '»'</i>👇🏻",
            reply_markup=buttons_food_05(db.get_client_temp_dish(user), length, numb)
        )
        db.set_client_can_alert(user, round(time.time()))
        db.set_client_temp_dish_id(user, db.restaurants_get_dish(rest[0], rest[1], dish['Название'])[0])
    else:
        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=f"🍤 <b>Кафе:</b>\n"
                 f"<i>«{rest[0]}», {rest[1]}</i>\n"
                 f"\n"
                 f"——— {icons[db.get_client_temp_category(user)]} <b>{db.get_client_temp_category(user)}</b> ———\n"
                 f"\n"
                 f"<b>Кажется, в этом заведении нет блюд, подходящих под ваши критерии</b> 🤔\n"
                 f"\n"
                 f"Попробуйте поменять категорию блюд, настроение или список продуктов, которые вы НЕ едите 😉\n"
                 f"\n {dish} {length} {numb}"
                 f"——— {icons[db.get_client_temp_mood(user)]} <b>{db.get_client_temp_mood(user)}</b> ———\n",
            # reply_markup=buttons_food_05(None, None, None)
        )
    db.set_users_mode(user, message_obj.message_id, 'food_category')


@dp.callback_query_handler(text_contains=f"send_dish")
async def send_dish(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')
    if db.get_users_ban(user):
        return None

    # Действие:

    if data[-1] == 'next':
        db.set_client_temp_dish(user, db.get_client_temp_dish(user) + 1)
    elif data[-1] == 'back':
        db.set_client_temp_dish(user, db.get_client_temp_dish(user) - 1)

    rest = db.get_client_temp_rest(user).split(':')
    dish, length, numb = menu.get_dish(user)

    ingredients = ""
    for ing in dish['Ингредиенты']:
        ingredients += f"• {str(ing).strip()}\n"

    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"🍤 <b>Кафе:</b>\n"
             f"<i>«{dish['Ресторан']}», {dish['Адрес']}</i>\n"
             f"\n"
             f"—— {icons[dish['Категория']]} <b>{dish['Категория']}</b> ——\n"
             f"\n"
             f"{icons[length - numb]} <i>«{dish['Название']}»</i>\n"
             f"\n"
             # f"🧾 <b>Ингредиенты:</b>\n"
             # f"<code>{ingredients}</code>\n"
             f"—— {icons[dish['Настроение']]} <b>{dish['Настроение']}</b> ——\n"
             f"\n"
             f"🗣️: <i>{dish['Описание']}</i>\n"
             f"\n"
             f"<i>Листайте блюда кнопками '«' и '»'</i>👇🏻",
        reply_markup=buttons_food_05(db.get_client_temp_dish(user), length, numb)
    )
    db.set_users_mode(user, message_obj.message_id, 'send_dish')
    db.set_client_can_alert(user, round(time.time()))
    db.set_client_temp_dish_id(user, db.restaurants_get_dish(rest[0], rest[1], dish['Название'])[0])


def buttons_food_05(dish: int | None, length: int | None, last: int | None):
    menu = InlineKeyboardMarkup(row_width=3)

    if dish is not None and length != 1:
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
    food_rec
    # menu_start
    btn1 = InlineKeyboardButton(text="« Поменять категорию",
                                callback_data="food_rec")

    btn2 = InlineKeyboardButton(text="«« Вернуться на главную",
                                callback_data="menu_start")

    btn3 = InlineKeyboardButton(text="Я выбрал(а) блюдо ‼️",
                                callback_data="search_dish")
    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)

    return menu

@dp.callback_query_handler(text_contains=f"bon_appetite")
async def bon_appetite(call: types.CallbackQuery):
    user = call.from_user.id
    mode = db.get_users_mode(user)['id']

    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"<blockquote>Приятного аппетита! ☺️🙏</blockquote>\nСпасибо, что воспользовался сервисом персональных рекомендаций блюд под настроение от <a href='https://t.me/food_2_mood'>food2mood</a>! 😃🤌",
        reply_markup=bon_appetite_keyboard(),
        parse_mode='HTML'
    )

    db.set_client_can_alert(user, 0)
    db.set_users_mode(user, mode, 'wrire_review')

    await asyncio.sleep(3600)  # Подождать 2 минуты
    await send_reminder_message(user)  # Отправить напоминалку

async def send_reminder_message(user_id):

    user_name = db.get_users_user_name(user_id)
    cafe = db.get_client_temp_rest(user_id)

    keyboard = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="Оставить отзыв о блюде", callback_data="search_dish")
    btn2 = InlineKeyboardButton(text="Не интересно", callback_data="menu_start")
    keyboard.add(btn1, btn2)

    await bot.send_message(
        chat_id=user_id,
        text=f"<b>{user_name}</b>, хочешь проконсультироваться по вопросам питания у нашего нутрициолога <strike>5000 руб/час</strike> совершенно бесплатно? 🤫🆓\n\nТогда оставь отзыв о кафе <b>{cafe}</b>!\n\nЗа эту активность мы начислим тебе f2m coin 🪙\n\n"
             f"Накопив определенное количество f2m coin, ты сможешь обменять их на консультацию у нашего нутрициолога 🧑‍⚕️🩺🥙",
        reply_markup=keyboard
    )

def bon_appetite_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="«« Вернуться на главную",
                                callback_data="menu_start")

    btn2 = InlineKeyboardButton(text="« Поменять категорию",
                                callback_data="food_rec")

    btn3 = InlineKeyboardButton(text="« Вернуться к рекомендациям", callback_data="send_dish")

    keyboard.row(btn1)
    keyboard.row(btn2)
    keyboard.row(btn3)
    return keyboard

import asyncio
from aiogram import types

@dp.callback_query_handler(text_contains="search_dish")
async def search_dish_global(call: types.CallbackQuery):
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
    db.set_users_mode(user, mode, 'wrire_review')

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

def buttons_food_05(dish: int | None, length: int | None, last: int | None):
    menu = InlineKeyboardMarkup(row_width=3)

    if dish is not None and length != 1:
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
    food_rec
    # menu_start
    btn1 = InlineKeyboardButton(text="« Поменять категорию",
                                callback_data="food_rec")

    btn2 = InlineKeyboardButton(text="«« Вернуться на главную",
                                callback_data="menu_start")

    btn3 = InlineKeyboardButton(text="Я выбрал(а) блюдо ‼️",
                                callback_data="bon_appetite")
    menu.add(btn1)
    menu.add(btn2)
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
        ingredients = ""
        for ing in dish['Ингредиенты'].split(','):
            ingredients += f"• {str(ing).strip()}\n"

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
        await qr_for_waiter.make_qrcode(dish['Название'])
        # db.set_client_can_alert(user, round(time.time()))
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
