from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

from main import dp, bot, db
import handlers.stop_lists as sl
import handlers.auxiliary_functions as af


def boss_menu():
    menu = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="⛔️СТОП-ЛИСТ", callback_data="boss_stop_list")
    btn2 = InlineKeyboardButton(text="📝ОФИЦИАНТЫ", callback_data="boss_waiters_stat")
    btn3 = InlineKeyboardButton(text="📶РЕКЛАМА", callback_data="boss_commercial")
    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)
    return menu


@dp.callback_query_handler(lambda call: call.data == "boss_commercial")
async def boss_commercial(call: types.CallbackQuery):
    try:
        boss_id = call.from_user.id
        rest = db.get_boss_rest(boss_id)
        total_click_count, current_click_count, total_guests_count, current_guests_count = af.total_and_current_counter(rest)
        text = (f"Статистика вовлеченности пользователей к заведению:\n\n"
                f"Кликабельность заведения через поиск: {total_click_count} ({current_click_count})\n\n"
                f"Обслужено гостей через f2m: {total_guests_count} ({current_guests_count})\n"
                "(В скобках статистика за смену с 00:00 до 23:59)")

        await bot.edit_message_text(chat_id=boss_id,
                                    message_id=call.message.message_id,
                                    text=text,
                                    reply_markup=InlineKeyboardMarkup().row(
                                        InlineKeyboardButton(text="Назад", callback_data="back_to_boss_menu")))
    except Exception as e:
        print(e)


@dp.callback_query_handler(lambda call: call.data == "boss_waiters_stat")
async def boss_waiters_stat(call: types.CallbackQuery):
    try:
        boss_id = call.from_user.id
        rest = db.get_boss_rest(boss_id)
        stats = db.get_waiters_names_and_stats(rest)
        text = "Общая статистика по официантам:\n\n"
        for waiter in stats:
            if None not in waiter:
                current_waiter_count = db.get_current_waiter_guests(rest, waiter[0])
                text += (f"{waiter[1]} {waiter[2]} {waiter[3]}\nКоличество уникальных заказов: {len(set(eval(waiter[4])))} "
                         f"({current_waiter_count})\n\n")
        text += "(В скобках статистика за смену с 00:00 до 23:59)"
        message_obj = await bot.edit_message_text(chat_id=boss_id,
                                    message_id=call.message.message_id,
                                    text=text,
                                    reply_markup=InlineKeyboardMarkup().row(
                                        InlineKeyboardButton(text="Назад", callback_data="back_to_boss_menu")))
        db.set_users_mode(boss_id, message_obj.message_id, 'boss_waiters_stat')
    except Exception as e:
        print(e)


@dp.callback_query_handler(lambda call: call.data == "boss_stop_list")
async def boss_stop_list(call: types.CallbackQuery):
    boss_id = call.from_user.id
    rest = db.get_boss_rest(boss_id)
    if not db.check_stop_list_exists(rest):
        db.create_stop_list(rest)
    await sl.set_stop_list(boss_id, "boss", call.message.message_id)


@dp.callback_query_handler(lambda call: call.data == "back_to_boss_menu")
async def back_to_boss_menu(call: types.CallbackQuery):
    await generate_boss_menu(call.from_user.id, call.message.message_id)


async def generate_boss_menu(boss_id, message_id=None):
    mode = db.get_users_mode(boss_id)
    text = ("Привет!\n\n"
            f"Это панель управления для менеджера заведения {db.get_boss_rest(boss_id)}\n\n"
            "/СТОП-ЛИСТ - добавление блюд в стоп-лист\n\n"
            "/ОФИЦИАНТЫ - статистика по работе официантов\n\n"
            "/РЕКЛАМА - статистика вовлеченности пользователей")
    if message_id or 'password' in mode['key']:
        message_obj = await bot.edit_message_text(chat_id=boss_id,
                                                  message_id=mode['id'],
                                                  text=text,
                                                  reply_markup=boss_menu())
        if 'password' in mode['key']:
            await bot.delete_message(chat_id=boss_id, message_id=mode['id']+1)
    else:
        message_obj = await bot.send_message(
            chat_id=boss_id,
            text=text,
            reply_markup=boss_menu()
        )
    db.set_users_mode(boss_id, message_obj.message_id, 'boss_menu')
