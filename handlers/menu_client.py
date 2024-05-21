import asyncio
import logging
import random
import os

import datetime
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

from main import dp, bot, db, config, Tools
admin = config()['telegram']['admin']


"""
Регистрация клиента
"""

@dp.callback_query_handler(text_contains=f"client_register")
async def client_register(call: types.CallbackQuery):
    user = call.from_user.id
    data = call.data.split('_')
    temp_rest = None
    if db.get_users_ban(user):
        return None

    # Действие:
    if data[-1] == 'again':
        try:
            temp_rest = db.get_client_temp_rest(user)
        except Exception as e:
            print(e)
        db.del_client(user)

    if not db.check_client(user):
        try:
            db.add_client(user, call.from_user.username)
            print("Успешно")
            try:
                db.set_client_temp_rest(user, temp_rest)
                print(temp_rest)
            except Exception as e:
                print(e)
        except:
            pass

    if len(data) > 2:
        if data[2] == 'sex':
            if data[3] == 'm':
                db.set_client_sex(user, 'Мужчина')
            if data[3] == 'w':
                db.set_client_sex(user, 'Женщина')
        elif data[2] == 'age':
            if data[3] == '18':
                db.set_client_age(user, '18')
            if data[3] == '25':
                db.set_client_age(user, '25')
            if data[3] == '35':
                db.set_client_age(user, '35')
            if data[3] == '45':
                db.set_client_age(user, '45')
            if data[3] == '45+':
                db.set_client_age(user, '45+')
        elif data[2] == 'style':
            if data[3] == 'normal':
                db.set_client_style(user, 'Стандартное')
            if data[3] == 'diet':
                db.set_client_style(user, 'Диетическое')
            if data[3] == 'veget':
                db.set_client_style(user, 'Вегетарианство')
            if data[3] == 'vegan':
                db.set_client_style(user, 'Веганство')
            if data[3] == 'raw':
                db.set_client_style(user, 'Сыроедение')

    if db.get_client_sex(user) == 'None':
        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=f"<b>🆔: Анкета поможет лучше понять тебя и твои вкусовые предпочтения! 🫶☺️</b>\n"
                    f"\n"
                    f"▶ Вопрос 1/4:\n"
                    f"\n"
                    f"<b>Какой ваш пол?</b>",
            reply_markup=buttons_client_00('sex')
        )
        db.set_users_mode(user, message_obj.message_id, 'client_register_sex')

    elif db.get_client_age(user) == 'None':
        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=f"<b>🆔: Анкета поможет лучше понять тебя и твои вкусовые предпочтения! 🫶☺️</b>\n"
                    f"\n"
                    f"▶ Вопрос 2/4:\n"
                    f"\n"
                    f"<b>Выберите свой возраст?</b>",
            reply_markup=buttons_client_00('age')
        )
        db.set_users_mode(user, message_obj.message_id, 'client_register_age')

    elif db.get_client_style(user) == 'None':
        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=f"<b>🆔: Анкета поможет лучше понять тебя и твои вкусовые предпочтения! 🫶☺️</b>\n"
                    f"\n"
                    f"▶ Вопрос 3/4:\n"
                    f"\n"
                    f"<b>Какой вы предпочитаете стиль питания?</b>",
            reply_markup=buttons_client_00('style')
        )
        db.set_users_mode(user, message_obj.message_id, 'client_register_style')
    elif call.data == 'client_register_ready':
        await bot.delete_message(user, call.message.message_id)
        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=int(db.get_users_mode(user)['id']),
            text=f"<b>Благодарим за регистрацию!</b>\n"
                    f"\n"
                    f"✅ Анкета заполнена! Теперь ты можешь получить персональные рекомендации по еде!",
            reply_markup=buttons_client_00('ready')
        )
        db.set_users_mode(user, message_obj.message_id, 'client_register_ready')
    elif call.data == 'client_register_e_ready':
        db.set_client_blacklist(user, "Пусто")
        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=int(db.get_users_mode(user)['id']),
            text=f"<b>Благодарим за регистрацию!</b>\n"
                    f"\n"
                    f"✅ Анкета заполнена! Теперь ты можешь получить персональные рекомендации по еде!",
            reply_markup=buttons_client_00('ready')
        )
        db.set_users_mode(user, message_obj.message_id, 'client_register_e_ready')

    elif db.get_client_blacklist(user) == 'None':
        message_obj = await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=f"<b>🆔: Анкета поможет лучше понять тебя и твои вкусовые предпочтения! 🫶☺️</b>\n"
                    f"\n"
                    f"▶ Вопрос 4/4:\n"
                    f"\n"
                    f"<b>Что вы НЕ едите?</b>\n"
                    f"\n"
                    f"<i>Напишите ответ одним сообщением в чат. А наш искусственный интеллект food2mood "
                 f"проанализирует запрос и пришлёт список продуктов для уточнения 😉✌️</i>",
            reply_markup=buttons_client_00('blacklist')
        )
        db.set_users_mode(user, message_obj.message_id, 'client_register_blacklist')
    else:
        await bot.delete_message(user, call.message.message_id)
        db.set_client_blacklist(user, None)




def buttons_client_00(mode: str):
    menu = InlineKeyboardMarkup(row_width=3)

    if mode == 'sex':
        btn1 = InlineKeyboardButton(text="Мужчина 🙋🏻‍♂",
                                    callback_data="client_register_sex_m")

        btn2 = InlineKeyboardButton(text="Женщина 🙋🏻‍♀",
                                    callback_data="client_register_sex_w")

        menu.row(btn1, btn2)

    elif mode == 'age':
        btn1 = InlineKeyboardButton(text="До 18",
                                    callback_data="client_register_age_18")

        btn2 = InlineKeyboardButton(text="18-25",
                                    callback_data="client_register_age_25")

        btn3 = InlineKeyboardButton(text="26-35",
                                    callback_data="client_register_age_35")

        btn4 = InlineKeyboardButton(text="36-45",
                                    callback_data="client_register_age_45")

        btn5 = InlineKeyboardButton(text="45+",
                                    callback_data="client_register_age_45+")

        menu.row(btn1)
        menu.row(btn2, btn3, btn4)
        menu.row(btn5)

    elif mode == 'style':
        btn1 = InlineKeyboardButton(text="Стандартное 🥘",
                                    callback_data="client_register_style_normal")

        btn2 = InlineKeyboardButton(text="Диетическое 🥗",
                                        callback_data="client_register_style_diet")

        btn3 = InlineKeyboardButton(text="Вегетарианство 🧀",
                                        callback_data="client_register_style_veget")

        btn4 = InlineKeyboardButton(text="Веганство 🥜",
                                        callback_data="client_register_style_vegan")

        btn5 = InlineKeyboardButton(text="Сыроедение 🥦",
                                        callback_data="client_register_style_raw")

        menu.row(btn1, btn2)
        menu.row(btn3, btn4)
        menu.row(btn5)

    elif mode == 'blacklist':
        btn1 = InlineKeyboardButton(text="Пропустить вопрос",
                                    callback_data="client_register_e_ready")

        menu.add(btn1)

    elif mode == 'ready':
        btn1 = InlineKeyboardButton(text="Выбрать настроение! 😌",
                                    callback_data="food_mood")

        menu.add(btn1)

    btn9 = InlineKeyboardButton(text="« Назад",
                                callback_data="menu_start")
    menu.add(btn9)

    return menu