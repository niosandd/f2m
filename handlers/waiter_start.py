import logging
import random

import datetime
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

from main import dp, bot, db, config, Tools

admin = config()['telegram']['admin']


def waiter_action(first_name, location):
    print(f"│ [{Tools.timenow()}] {first_name} → {location}")


def ind_to_number(ind):
    numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    result = ""
    for char in str(ind):
        result += numbers[int(char)]
    return result


async def start(message: types.Message):
    waiter = message.from_user.id
    try:
        info = message.text.split("/")
        name = info[0].split()
        rest = info[1]
        # Новый официант:
        if not db.check_waiter_exists(waiter):
            # Регистрируем официанта:
            db.add_waiter(
                waiter,
                rest,
                f'tg://user?id={waiter}',
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
                   f'\nid <a href="tg://user?id={waiter}">{waiter}</a>' \
                   f'\n'
            await bot.send_message(waiter, text)
        else:
            text = f'\nТы уже зарегистрировался(ась) как официант'
            await bot.send_message(waiter, text)
    except Exception:
        text = f'\nОшибка ввода ФИО/ресторан'
        await bot.send_message(waiter, text)


async def get_order(message: types.Message, client_id):
    waiter = message.from_user.id
    # Проверяем официанта:
    if db.check_waiter_exists(waiter):
        temp_rest = db.get_client_temp_rest(client_id)
        db.set_client_temp_rest(waiter, temp_rest)
        try:
            await set_order(waiter, client_id)
        except Exception as e:
            print(e)


def order_status():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="+", switch_inline_query_current_chat='')
    btn2 = InlineKeyboardButton(text="-", callback_data="d_from_order")
    btn3 = InlineKeyboardButton(text="Принять заказ", callback_data="order_accepted")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup


async def dish_added(waiter, dish_id):
    client_id = eval(db.get_waiter_score(waiter))[-1]
    dish = db.restaurants_get_by_id(dish_id)[4]
    mode = db.get_users_mode(waiter)
    try:
        basket = eval(db.get_basket(client_id))
    except Exception as e:
        print("waiter error", e)
        basket = {}
    basket[dish] = dish_id
    db.set_basket(client_id, str(basket))
    await set_order(waiter, client_id, message_id=mode['id'])


@dp.callback_query_handler(text_contains=f"d_from_order")
async def d_from_order(call: types.CallbackQuery):
    waiter = call.from_user.id
    client_id = eval(db.get_waiter_score(waiter))[-1]
    data = call.data.split('_')
    try:
        basket = eval(db.get_basket(client_id))
    except Exception as e:
        print("waiter error", e)
        basket = {}
    if len(data) > 3:
        dish_id = data[-1]
        dish = db.restaurants_get_by_id(dish_id)[4]
        try:
            basket.pop(dish, None)
            db.set_basket(client_id, str(basket))
        except ValueError:
            pass
    await bot.edit_message_text(chat_id=waiter,
                                message_id=call.message.message_id,
                                text="Нажмите на позицию чтобы удалить",
                                reply_markup=change_order(basket))


def change_order(basket):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for dish in basket:
        btn = InlineKeyboardButton(text=str(dish),
                                   callback_data=f"d_from_order_{basket[dish]}")
        keyboard.row(btn)
    btn1 = InlineKeyboardButton(text="Назад", callback_data="back_to_order")
    keyboard.row(btn1)
    return keyboard


@dp.callback_query_handler(text_contains=f"back_to_order")
async def back_to_order(call: types.CallbackQuery):
    waiter = call.from_user.id
    client_id = eval(db.get_waiter_score(waiter))[-1]
    await set_order(waiter, client_id, message_id=call.message.message_id)


@dp.callback_query_handler(text_contains=f"order_accepted")
async def order_accepted(call: types.CallbackQuery):
    waiter = call.from_user.id
    client_id = eval(db.get_waiter_score(waiter))[-1]
    if not db.get_waiter_score(waiter):
        temp_list = [client_id]
    else:
        temp_list = eval(db.get_waiter_score(waiter))
        temp_list.append(client_id)
    db.set_waiter_score(waiter, str(temp_list))
    text = "Заказ принят!\n" \
           f'\n <b>Количество твоих уникальных заказов: {len(set(temp_list))}</b>'
    await bot.edit_message_text(chat_id=waiter, message_id=call.message.message_id, text=text)


async def set_order(waiter, client_id, message_id=None):
    temp_list = eval(db.get_waiter_score(waiter))
    try:
        basket = list(eval(db.get_basket(client_id)).keys())
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
    if message_id:
        message_obj = await bot.edit_message_text(chat_id=waiter,
                                                  message_id=message_id,
                                                  text=text,
                                                  reply_markup=order_status())
    else:
        message_obj = await bot.send_message(chat_id=waiter, text=text, reply_markup=order_status())
    db.set_users_mode(waiter, message_obj.message_id, 'get_order')
