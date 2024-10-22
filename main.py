from uuid import uuid4
import logging
import qrcode
from PIL import Image
import asyncio
import datetime
import time
import logging
from datetime import datetime
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.deep_linking import decode_payload

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    ReplyKeyboardMarkup, InlineQuery, InputTextMessageContent, InlineQueryResultArticle
from pytz import timezone
import ccxt.async_support as ccxt
import json
import requests

import normalize
from my_libraries import Tools
from help import config
from db import Database
#import chat_gpt

db = Database('files/db_users.db')

""" 
Загрузка глобальных переменных.
"""

log = Tools.Log('log.log')
reviews = config()['telegram']['reviews']

icons = {
    "Салаты и закуски": "🥗",
    "Первые блюда": "🍲",
    "Горячие блюда": "🍛",
    "Гарниры": "🍚",
    "Напитки": "☕",
    "Завтрак": "🍳",
    "Ужин": "🍽️",
    "Японская кухня": "🍣",
    "Поке": "🥢",
    "Холодные закуски": "😋🧊",
    "Салаты": "🥗",
    "Супы": "🍲",
    "Закуски": "😋",
    "Горячие закуски": "😋🔥",
    "Десерты": "🍰",
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
}

try:
    bot = Bot(token=config()['telegram']['api'], parse_mode='HTML',
              protect_content=False)
except:
    print("Заполните файл config.json правильно!")
    time.sleep(10000000)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
main_loop = asyncio.get_event_loop()

last_time = {}
time_wait = 1000  # Задержка в мс

"""
Работа с командами ТГ-бота.
"""

import handlers.menu_start as m_start
import handlers.waiter_start as w_start
import handlers.bosses as bosses
import handlers.menu_client as m_settings
import handlers.menu_food as m_food



class ActionLoggingMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        try:
            user_id = None
            action = None

            if update.message:
                user_id = update.message.from_user.id
                if update.message.text == '/start':
                    action = 'Запуск бота'
                elif update.message.text == '/form':
                    action = 'Пользователь прошел тест на выявление вкусовых предпочтений'
                else:
                    if update.message.text:
                        action = f"Пользователь отправил сообщение: {update.message.text}"
                    else:
                        action = "Сообщение без текста"
            elif update.callback_query:
                user_id = update.callback_query.from_user.id
                if update.callback_query.data == 'confirmation_of_the_questionnaire':
                    action = f"Пользователь подтвердил свою анкету"
                if update.callback_query.data == 'food_mood':
                    action = f"Пользователь перешел к выбору настроения"
                if update.callback_query.data in ["food_choose_get_Радость", "food_choose_get_Печаль", "food_choose_get_Гнев", "food_choose_get_Спокойствие", "food_choose_get_Волнение"]:
                    action = "Пользователь выбрал свое настроение"
                if update.callback_query.data == 'client_register_again':
                    action = 'Пользователь перешел в меню редактирование анкеты'
                if 'rewiew_star' in update.callback_query.data:
                    action = 'Пользователь поставил оценку на блюдо'
                if update.callback_query.data == 'food_mood':
                    action = 'Пользователь захотел получить рекомендацию'
                if update.callback_query.data == 'menu_start':
                    action = 'Пользователь вернулся в главное меню'
                if update.callback_query.data == 'food_to_mood_coin_status':
                    action= 'Пользователь проверяет количество своих коинов'
                if update.callback_query.data == 'leave_a_review':
                    action = 'Пользователь оставил отзыв'
                if 'client_register_style' in update.callback_query.data:
                    action = 'Пользователь выбрал стиль питания'
                if 'food_category_' in update.callback_query.data:
                    action = f'Пользователь перешел в категорию {update.callback_query.data.split("food_category_")[1]}'
                if update.callback_query.data in ['back_to_categories', 'show_categories', 'show_categories_again']:
                    action = 'Пользователь перешел к меню по категориям'
                if update.callback_query.data == 'basket_add':
                    action = 'Пользователь добавил блюдо в корзину'
                if update.callback_query.data == 'basket_remove':
                    action = 'Пользователь удалил блюдо из корзины'
                if update.callback_query.data == 'check_order':
                    action = 'Пользователь нажал на кнопку сделать заказ'
                if update.callback_query.data == 'create_qr':
                    action = 'Пользователь оформил заказ'
                if 'bon_appetite' in update.callback_query.data:
                    action = 'После оформления заказа пользователь нажал на кнопку "Готово!"'
                if 'send_dish_del' in update.callback_query.data:
                    action = 'Пользователь вернулся к рекомендациям"'


            if user_id and action:
                if not db.check_last_action(user_id, action):
                    db.add_user_action(user_id, action)
                    logging.info(f"Пользователь {user_id} совершил действие: {action}")
        except Exception as e:
            print("Ошибка клиентского пути:", e)

dp.middleware.setup(ActionLoggingMiddleware())

@dp.message_handler(commands=['start', 'restart'])
async def start(message: types.Message):
    user = message.from_user.id
    if "or" in decode_payload(message.get_args()):
        await w_start.get_order(message, decode_payload(message.get_args())[2:])
    elif db.check_users_user_exists(message.from_user.id):
        print(f"│ [{Tools.timenow()}] {message.from_user.first_name} → Меню")
        if not db.get_users_ban(message.from_user.id):
            try:
                await m_start.start(message)
                try:
                    if not db.check_client(user):
                        db.add_client(user, message.from_user.username)
                    rest_name = decode_payload(message.get_args())[4:]
                    rest_address = db.restaurants_find_address(rest_name)
                    db.set_client_last_qr_time(user, round(time.time()))
                    if "rest" in decode_payload(message.get_args()):
                        db.set_client_temp_rest(user, f"{rest_name}:{rest_address}")
                        if db.check_basket_exists(user):
                            db.set_basket(user, "{}")
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
        else:
            await bot.send_message(
                chat_id=user,
                text="\n🚫 <b>Ваш аккаунт был временно заблокирован!</b>"
                     "\n"
                     "\n<i>Уважаемый пользователь,"
                     "\nМы заметили некоторую подозрительную активность, связанную с вашей учетной записью, и в целях обеспечения безопасности мы временно приостановили доступ к вашему аккаунту.</i>"
            )
    else:
        print(f"│ [{Tools.timenow()}] NEW {message.from_user.first_name} → Меню")
        await m_start.start(message)
        try:
            if not db.check_client(user):
                db.add_client(user, message.from_user.username)
            rest_name = decode_payload(message.get_args())[4:]
            rest_address = db.restaurants_find_address(rest_name)
            db.set_client_last_qr_time(user, round(time.time()))
            if "rest" in decode_payload(message.get_args()):
                db.set_client_temp_rest(user, f"{rest_name}:{rest_address}")
                if db.check_basket_exists(user):
                    db.set_basket(user, "{}")
        except Exception as e:
            print(e)


@dp.message_handler(commands=['waiter'])
async def waiter(message: types.Message):
    user = message.from_user.id
    if not db.check_waiter_exists(user):
        message_obj = await bot.send_message(
            chat_id=user,
            text="Пожалуйста, введи свое ФИО/название ресторана в формате: "
                 "Иванов Иван Иванович/Блан де Блан"
        )
        db.set_users_mode(user, message_obj.message_id, 'waiter_reg')
    else:
        text = f'\nТы уже зарегистрировался(ась) как официант'
        await bot.send_message(user, text)


@dp.message_handler(commands=['boss_mldzh'])
async def boss_mldzh(message: types.Message):
    user = message.from_user.id
    if not db.check_boss_exists(user):
        await bosses.generate_boss_menu(user)
    else:
        db.add_boss(user, db.get_client_temp_rest(user))
        await bosses.generate_boss_menu(user)
        # text = f'\nТы не зарегистрирован(ана) как менеджер заведения'
        # await bot.send_message(user, text)


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    user = message.from_user.id
    if user in [375565156, 1004320969, 803124861, 6728666475]:
        message_obj = await bot.send_message(
            chat_id=user,
            text="Отправьте рассылаемое сообщение в этот чат, после чего выберите режим оповещения",
        )
        db.set_users_mode(user, message_obj.message_id, 'notification')
    else:
        await bot.send_message(user, "Отсутствуют права доступа")


def notification(original_message_id):
    menu = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="Всем пользователям", callback_data=f'user_notification_{original_message_id}')
    btn2 = InlineKeyboardButton(text="Официантам", callback_data=f'waiter_notification_{original_message_id}')
    menu.add(btn1)
    menu.add(btn2)
    return menu


@dp.callback_query_handler(text_contains=f"notification")
async def send_notification(call: types.CallbackQuery):
    try:
        data = call.data.split('_')
        original_id = call.from_user.id
        original_message_id = int(data[-1])
        users = []
        if "user" in data:
            users = db.get_users_users()
        elif "waiter" in data:
            users = db.get_waiters_waiters()
        for id in users:
            try:
                await bot.forward_message(chat_id=id, from_chat_id=original_id, message_id=original_message_id)
            except Exception as e:
                print(e)
                continue
        await bot.send_message(chat_id=original_id, text="Рассылка завершена")
        await bot.delete_message(chat_id=original_id, message_id=call.message.message_id)
    except Exception as e:
        print(e)


@dp.message_handler(commands=['mldzh'])
async def mldzh(message: types.Message):
    user = message.from_user.id
    if db.get_users_ban(user):
        return None
    db.set_client_temp_rest(user, None)
    if db.check_basket_exists(user):
        db.set_basket(user, "{}")
    try:
        await bot.delete_message(user, message.message_id)
    except Exception as e:
        print(e)
    message_obj = await bot.send_message(
        chat_id=user,
        text=f"<b>Выбери заведение в поиске, чтобы посмотреть меню👇🏻\n</b>",
        reply_markup=buttons_food_x()
    )
    db.set_users_mode(user, message_obj.message_id, 'food_inline_handler_x')


def buttons_food_x():
    menu = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton(text="🔎 Поиск кафе", switch_inline_query_current_chat='')
    menu.add(btn1)
    return menu


@dp.message_handler(commands=['f2m_coins'])
async def f2m_coins(message: types.Message):
    user = message.from_user.id
    mode = db.get_users_mode(user)['id']
    username = db.get_users_user_first_name(user)
    coin_counter = db.get_users_food_to_mood_coin(user)
    await bot.send_message(
        chat_id=user,
        text=f"{username}, количество твоих <i>f2m коинов</i> составляет: <b>{coin_counter}</b> \n\n"
             f"<b>Спасибо за активность! Так держать!🚀🔥</b>\n\n"
             f"<i>Проверь, можешь обменять такое количество на бесплатную консультацию от нутрициолога по кнопке внизу👇🧑‍⚕️🆓</i>",
        reply_markup=consult_coin_keyboard()
    )
    db.set_users_mode(user, mode, "food_to_mood_status")
    db.add_user_action(user, 'Пользователь проверил свои f2m_coins')
    # await bot.send_message(user, text="https://t.me/food_2_mood/55")


@dp.inline_handler()
async def food_restaurant_search(inline_query: InlineQuery):
    user = inline_query.from_user.id
    mode = db.get_users_mode(user)
    # Поиск ресторана
    if 'food_inline_handler' in mode['key']:
        db.add_user_action(user, 'Пользователь ищет кафе через поиск')
        if len(str(inline_query.query)) > 0:
            print(f'│ [{Tools.timenow()}] Пользователь ищет кафе... {str(inline_query.query)}')
            posts = db.restaurants_find_all(str(inline_query.query).lower().capitalize())
        else:
            posts = db.restaurants_get_all()

        results = []
        if not posts:
            result = InlineQueryResultArticle(
                id='0',
                title=f"Кафе в базе нет 😔",
                description="Нажмите, чтобы добавить кафе ⬅",
                input_message_content=InputTextMessageContent(f'Кафе в базе нет 😔'),
            )
            results.append(result)
            db.set_users_mode(user, db.get_users_mode(user)['id'], 'food_inline_handler_empty')
        else:
            for post in posts:
                result = InlineQueryResultArticle(
                    id=post[0],
                    title=f"«{post[1]}»",
                    description=post[2],
                    input_message_content=InputTextMessageContent(f'{post[1]}:{post[2]}'),
                )
                results.append(result)
            db.set_users_mode(user, db.get_users_mode(user)['id'], mode['key'])

        await inline_query.answer(results, cache_time=1)

    # Поиск блюда
    elif mode['key'] == 'write_review':
        db.add_user_action(user, 'Пользователь ищет блюдо через поиск')
        rest_name = db.get_client_temp_rest(user).split(':')[0]
        if len(str(inline_query.query)) > 0:
            print(f'│ [{Tools.timenow()}] Пользователь ищет блюдо... {str(inline_query.query)}')
            posts = db.restaurants_find_dish(rest_name, str(inline_query.query).lower().capitalize())
        else:
            posts = db.restaurants_get_all_dish(rest_name)

        results = []
        if len(posts) == 0:
            result = InlineQueryResultArticle(
                id='0',
                title=f"Такого блюда в базе нет 🤔",
                description="Попробуйте ввести другое название",
                input_message_content=InputTextMessageContent(
                    f'Такого блюда в базе нет 🤔\nПопробуйте ввести другое название'),
            )
            results.append(result)
            await inline_query.answer(results, cache_time=1)
        else:
            for post in posts:
                result = InlineQueryResultArticle(
                    id=post[0],
                    title=f"«{post[1]}»: «{post[3]}»",
                    description=post[2],
                    input_message_content=InputTextMessageContent(f'{post[1]}:{post[2]}:{post[3]}'),
                )
                results.append(result)
            await inline_query.answer(results[:10], cache_time=1)

    elif mode['key'] == "get_order" or mode['key'] == "set_stop_list":
        db.add_user_action(user, 'Пользователь хочет оформить заказ')
        rest_name = db.get_client_temp_rest(user).split(':')[0]
        if len(str(inline_query.query)) > 0:
            posts = db.restaurants_find_dish(rest_name, str(inline_query.query).lower().capitalize())
        else:
            posts = db.restaurants_get_all_dish(rest_name)

        results = []
        if len(posts) == 0:
            result = InlineQueryResultArticle(
                id='0',
                title=f"Такого блюда в базе нет 🤔",
                description="Попробуйте ввести другое название",
                input_message_content=InputTextMessageContent(
                    f'Такого блюда в базе нет 🤔\nПопробуйте ввести другое название'),
            )
            results.append(result)
            await inline_query.answer(results, cache_time=1)
        else:
            for post in posts:
                result = InlineQueryResultArticle(
                    id=post[0],
                    title=f"«{post[1]}»: «{post[3]}»",
                    description=post[2],
                    input_message_content=InputTextMessageContent(f'{post[1]}:{post[2]}:{post[3]}'),
                )
                results.append(result)
            await inline_query.answer(results[:10], cache_time=1)


@dp.message_handler(content_types=["any"])
async def bot_message(message):
    user = message.from_user.id
    mode = db.get_users_mode(user)

    if message.text not in ['/start', '/waiter', '/admin', '/mldzh', '/f2m_coins']:

        # Чёрный список продуктов
        if mode['key'] == 'client_register_blacklist':
            await client_register_blacklist(user, message)

        # Запросить заведение
        if mode['key'] == 'food_inline_handler_empty':
            await bot.send_message(
                chat_id=user,
                text="Пришлите интересующее вас заведение в наш чат @jul_lut, мы будем вам очень благодарны ✨",
                reply_markup=buttons_00()
            )

        # Выбор ресторана из поиска
        if mode['key'] == 'food_inline_handler':
            await m_food.food_rec_get(user, message)
            db.add_user_action(user, 'Пользователь выбирает ресторан из поиска')

        if mode['key'] == 'food_inline_handler_x':
            db.add_user_action(user, 'Пользователь выбирает другой ресторан')
            data = message.text.split(':')
            db.set_client_temp_rest(user, f"{data[0]}:{data[1]}")
            db.set_client_temp_recommendation(user, None)
            if db.check_basket_exists(user):
                db.set_basket(user, "{}")
            try:
                await bot.delete_message(user, mode['id'])
            except Exception as e:
                print(e)
            await bot.send_message(
                chat_id=user,
                text=f"Ресторан успешно установлен",
                reply_markup=get_to_menu()
            )

        if mode['key'] == 'food_inline_handler_y':
            data = message.text.split(':')
            db.set_client_temp_rest(user, f"{data[0]}:{data[1]}")
            db.set_client_temp_recommendation(user, None)
            if db.check_basket_exists(user):
                db.set_basket(user, "{}")
            await m_food.food_rec2(user, "food_rec_Нутрициолог".split('_'))

        if mode['key'] == "waiter_reg":
            await w_start.start(message)

        if mode['key'] == "get_order":
            dish = message.text.split(':')
            dish_id = db.restaurants_get_dish(dish[0], dish[1], dish[2])[0]
            await w_start.dish_added(user, dish_id)

        if mode['key'] == "set_stop_list":
            dish = message.text.split(':')
            dish_id = db.restaurants_get_dish(dish[0], dish[1], dish[2])[0]
            await bosses.dish_added(user, dish_id)

        if mode['key'] == "notification":
            await bot.send_message(
                chat_id=user,
                text="Выберите режим оповещения",
                reply_markup=notification(message.message_id)
            )


        # Выбор блюда из поиска
        if mode['key'] == 'write_review':
            dish = message.text.split(':')
            dish_id = db.restaurants_get_dish(dish[0], dish[1], dish[2])[0]
            db.set_client_temp_dish_id(user, dish_id)
            await choose_dish(dish_id, message)

        # Отправить отзыв
        if mode['key'] == 'type_review':
            await dp.storage.set_data(user=user, data={'review': message.text})
            user_data = await dp.storage.get_data(user=user)
            unique_uuid = uuid4
            username = message.from_user.username
            rating = user_data.get('rating')
            review = user_data.get('review')
            dish_name = user_data.get('dish_name')
            restaurant_name = user_data.get('restaurant_name')
            print("got message")
            # await bot.send_message(
            #     chat_id=reviews,
            #     text=f"⭐️ Новый отзыв от id<code>{user}</code>:\n"
            #          f"\n"
            #          f"<i>{message.text}</i>"
            # )
            await bot.delete_message(user, message.message_id)
            await bot.edit_message_text(
                chat_id=user,
                message_id=mode['id'],
                text=f"<b>Спасибо за отзыв! 🤜🤛</b>\n\n Проверь количество <code>f2m коины</code> у себя в личном кабинете!\n"
                     f"<blockquote>Мы будем ждать тебя на консультации у нашего нутрициолога 🧑‍⚕️🩺🍏</blockquote>",
                reply_markup=buttons_02()
            )
            db.add_user_action(user, 'Пользователь оставил отзыв')

            if len(message.text.split()) >= 10:
                coin_counter = 2
                await db.add_food_to_mood_coin(user, coin_counter)
            else:
                coin_counter = 1
                await db.add_food_to_mood_coin(user, coin_counter)
            db.set_new_review(unique_uuid, username, rating, review, dish_name, restaurant_name)
            db.restaurants_set_review(db.get_client_temp_dish_id(user), message.text)
            db.set_users_mode(user, mode['id'], '')
    try:
        if mode['key'] not in ["notification"]:
            await bot.delete_message(user, message.message_id)
    except:
        pass


async def client_register_blacklist(user, message: types.Message):
    message_obj = await message.answer(
        text=f"Одну секунду... ⏳"
    )
    # products = str(chat_gpt.send_message(message.text)).strip('"')
    products = normalize.normal_list(message.text)
    db.set_client_blacklist(user, products)
    await bot.edit_message_text(
        chat_id=user,
        message_id=message_obj.message_id,
        text=f"<b>Эти продукты ты не употребляешь в пищу:</b>\n"
             f"<code>{products}</code>\n"
             f"\n"
             f"Всё верно?",
        reply_markup=buttons_01()
    )
    db.add_user_action(user, 'Пользователь составил свой блэклист продуктов')


def buttons_00():
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="Хорошо! Удалить это сообщение.",
                                callback_data="temp_del")

    menu.add(btn1)

    return menu


def buttons_01():
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="Да, всё верно 👍🏻",
                                callback_data="client_register_ready")

    btn2 = InlineKeyboardButton(text="Нет! Сейчас напишу заново 👎🏻",
                                callback_data="client_register_notready")

    menu.add(btn1)
    menu.add(btn2)

    return menu


def buttons_02():
    menu = InlineKeyboardMarkup(row_width=2)

    btn1 = InlineKeyboardButton(text="« Вернуться на главную",
                                callback_data="menu_start")

    btn2 = InlineKeyboardButton(text="Оставить ещё один отзыв", callback_data="leave_a_review")

    btn3 = InlineKeyboardButton(text="Мои f2m коины 🪙", callback_data="food_to_mood_coin_status")

    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)

    return menu


def get_to_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="« Вернуться на главную",
                                callback_data="menu_start")

    keyboard.add(btn1)
    return keyboard


"""
Вспомогательные функции.
"""


@dp.callback_query_handler(text_contains=f"food_to_mood_coin_status")
async def coin_status(call: types.CallbackQuery):
    user = call.from_user.id
    mode = db.get_users_mode(user)['id']
    username = db.get_users_user_first_name(user)
    coin_counter = db.get_users_food_to_mood_coin(user)
    await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=f"{username}, количество твоих <i>f2m коинов</i> составляет: <b>{coin_counter}</b> \n\n"
             f"<b>Спасибо за активность! Так держать!🚀🔥</b>\n\n"
             f"<i>Проверь, можешь обменять такое количество на бесплатную консультацию от нутрициолога по кнопке внизу👇🧑‍⚕️🆓</i>",
        reply_markup=consult_coin_keyboard()
    )
    db.set_users_mode(user, mode, "food_to_mood_status")
    db.add_user_action(user, 'Пользователь проверяет количество своих коинов')


@dp.callback_query_handler(text_contains=f"coin_exchange")
async def coin_exchange(call: types.CallbackQuery):
    user = call.from_user.id
    mode = db.get_users_mode(user)['id']
    await bot.send_message(chat_id=user,
                           text=f"<a href='https://t.me/food_2_mood/58'>Тут описание, как обменять коины на консультацию</a>",
                           reply_markup=get_to_menu())
    db.set_users_mode(user, mode, "coin_exchange")
    db.add_user_action(user, 'Пользователь захотел обменять коины на консультацию')
    # Удаление сообщения из coin_status
    await bot.delete_message(chat_id=user, message_id=call.message.message_id)


def consult_coin_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn1 = InlineKeyboardButton(text="Обменять на бесплатную консультацию", url="https://t.me/food_2_mood/61")
    btn2 = InlineKeyboardButton(text="« Вернуться на главную", callback_data="menu_start")
    keyboard.row(btn1)
    keyboard.row(btn2)
    return keyboard


@dp.callback_query_handler(text_contains=f"temp_del")
async def temp_del(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')
    await bot.delete_message(user, call.message.message_id)


async def checker():
    while True:
        # await asyncio.sleep(5 - time.time() % 60)
        await asyncio.sleep(10)

        for client in db.all_client():
            try:
                client_id = client[0]
                client_alert = client[-1]
                if client_alert == 0:
                    continue

                if round(time.time()) > client_alert + 60 * 30 - 60:
                    # if True:
                    mode = db.get_users_mode(client_id)
                    message_obj = await bot.send_message(
                        chat_id=client_id,
                        text=f"Благодарим, что воспользовались рекомендациями food mood! 🤌🏻\n"
                             f"\n"
                             f"Оцени блюдо, которое ты взял в данном заведении! "
                             f"Это поможет нам с анализом ваших вкусовых предпочтений "
                             f"и окажет влияние на ваши персональные рекомендации "
                             f"в будущем 😏🔮",
                        reply_markup=buttons_03()
                    )
                    db.set_client_can_alert(client_id, 0)
                    db.set_users_mode(client_id, message_obj.message_id, 'write_review')
            except BaseException as ex:
                print(f"│ Не получилось попросить отзыв: {ex}")


async def choose_dish(dish_id, message: types.Message):
    user = message.from_user.id
    if db.get_users_ban(user):
        return None

    # Действие:
    mode = db.get_users_mode(user)
    dish = db.restaurants_get_by_id(dish_id)

    message_obj = await bot.send_message(
        chat_id=user,
        text=f"🍤 <b>Кафе:</b>\n"
             f"<i>«{dish[1]}», {dish[2]}</i>\n"
             f"\n"
             f"💫 Блюдо:\n"
             f"<i>«{dish[4]}»</i>\n"
             f"\n"
             f"Оцените блюдо по шкале от 1 до 5 👇🏻",
        reply_markup=buttons_04(dish_id)
    )
    db.set_users_mode(user, mode['id'], 'review')


def buttons_03():
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="🔎 Выбрать блюдо", switch_inline_query_current_chat='')
    btn2 = InlineKeyboardButton(text="Получить рекомендации! 🍤", callback_data="food_mood")
    btn3 = InlineKeyboardButton(text="Заполнить анкету заново 📋", callback_data="client_register_again")

    menu.row(btn1)
    menu.row(btn2)
    menu.row(btn3)

    return menu


def buttons_04(dish_id):
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="1 ⭐",
                                callback_data=f"review_star_1_{dish_id}")

    btn2 = InlineKeyboardButton(text="2 ⭐",
                                callback_data=f"review_star_2_{dish_id}")

    btn3 = InlineKeyboardButton(text="3 ⭐",
                                callback_data=f"review_star_3_{dish_id}")

    btn4 = InlineKeyboardButton(text="4 ⭐",
                                callback_data=f"review_star_4_{dish_id}")

    btn5 = InlineKeyboardButton(text="5 ⭐",
                                callback_data=f"review_star_5_{dish_id}")

    menu.row(btn1, btn2, btn3, btn4, btn5)

    return menu


@dp.callback_query_handler(text_contains=f"review_end")
async def review_end(call: types.CallbackQuery):
    current_time = round(time.time())
    user = call.from_user.id
    user_data = await dp.storage.get_data(user=user)
    data = call.data.split('_')
    if db.get_users_ban(user):
        return None

    coin_counter = 1
    unique_uuid = uuid4
    username = call.from_user.username
    rating = user_data.get('rating')
    review = ""
    dish_name = user_data.get('dish_name')
    restaurant_name = user_data.get('restaurant_name')

    mode = db.get_users_mode(user)
    await bot.edit_message_text(
        chat_id=user,
        message_id=mode['id'],
        text=f"<b>Спасибо за отзыв! 🤜🤛</b>\n\n Проверь количество <code>f2m коины</code> у себя в личном кабинете!\n"
             f"<blockquote>Мы будем ждать тебя на консультации у нашего нутрициолога 🧑‍⚕️🩺🍏</blockquote>️",
        reply_markup=buttons_02()
    )
    db.add_user_action(user, 'Пользователь оставил отзыв')
    await db.add_food_to_mood_coin(user, coin_counter)
    db.set_new_review(unique_uuid, user, username, rating, review, dish_name, restaurant_name)
    # db.set_users_last_recomendation_time(user, current_time)
    db.set_users_mode(user, mode['id'], '')



@dp.callback_query_handler(text_contains=f"review_star")
async def review_star(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')
    rating = data[-2]
    # await dp.storage.set_data(user=user, data={'rating': rating})

    if db.get_users_ban(user):
        return None

        # Действие:
    mode = db.get_users_mode(user)
    dish_id = int(data[-1])
    dish = db.restaurants_get_by_id(dish_id)
    db.restaurants_set_rating(dish_id, int(data[-2]))
    await dp.storage.set_data(user=user, data={
        'rating': rating,
        'dish_name': dish[4],
        'restaurant_name': dish[1]
    })

    # Удаление предыдущего сообщения
    await call.message.delete()

    message_obj = await bot.send_message(
        chat_id=user,
        text=f"🍤 <b>Кафе:</b>\n"
             f"<i>«{dish[1]}», {dish[2]}</i>\n"
             f"\n"
             f"💫 Блюдо:\n"
             f"<i>«{dish[4]}»</i>\n"
             f"\n"
             f"Если хотите оставить письменный отзыв, напиши его в ответ на это сообщение 🙏🏻\n"
             f"\n"
             f"Спасибо!",
        reply_markup=buttons_05()
    )
    db.set_users_mode(user, message_obj.message_id, 'type_review')
    db.add_user_action(user, 'Пользователь оставил отзыв')

def buttons_05():
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="Пропустить",
                                callback_data=f"review_end")

    menu.row(btn1)

    return menu


"""
Запуск.
"""


async def main():
    print(Tools.Color().send_contact())
    print("╭─")
    # asyncio.create_task(checker())


if __name__ == '__main__':
    try:
        from handlers import dp

        loop = asyncio.get_event_loop()
        loop.create_task(main())
        executor.start_polling(dp)
    except BaseException as ex:
        log.log_critical('DUMP!!!', True)
        time.sleep(1000000)
