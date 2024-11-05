from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

from main import dp, bot, db, config, Tools
import handlers.stop_lists as sl
import handlers.auxiliary_functions as af

async def generate_admin_menu(admin_id, rest=None, message_id=None):
    if not db.check_admin_exists(admin_id):
        db.add_admin(admin_id, rest)
    elif rest:
        db.set_admin_rest(admin_id, rest)
    text = "Какая информация вас интересует: "
    if message_id:
        message_obj = await bot.edit_message_text(chat_id=admin_id,
                                                  message_id=message_id,
                                                  text=text,
                                                  reply_markup=admin_menu())
    else:
        message_obj = await bot.send_message(
            chat_id=admin_id,
            text=text,
            reply_markup=admin_menu()
        )
    db.set_users_mode(admin_id, message_obj.message_id, 'admin_menu')
    
    
def admin_menu():
    menu = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="СТОП-ЛИСТ", callback_data="admin_stop_list")
    btn2 = InlineKeyboardButton(text="ОФИЦИАНТЫ", callback_data="admin_waiters_stat")
    btn3 = InlineKeyboardButton(text="РЕКЛАМА", callback_data="admin_commercial")
    btn4 = InlineKeyboardButton(text="ОТЗЫВЫ", callback_data="admin_reviews")
    btn5 = InlineKeyboardButton(text="РАССЫЛКА", callback_data="admin_notification")
    menu.add(btn1, btn2, btn3, btn4, btn5)
    return menu


@dp.callback_query_handler(lambda call: call.data == "admin_waiters_stat")
async def admin_waiters_stat(call: types.CallbackQuery):
    try:
        admin_id = call.from_user.id
        rest = db.get_admin_rest(admin_id)
        stats = db.get_waiters_names_and_stats(rest)
        current_waiter_count = 0 # ВРЕМЕННО ПОКА НЕ ВВЕЛИ СМЕНЫ
        text = "Общая статистика по официантам:\n\n"
        for waiter in stats:
            if None not in waiter:
                text += (f"{waiter[1]} {waiter[2]} {waiter[3]}\nКоличество уникальных заказов: {len(set(eval(waiter[4])))} "
                         f"({current_waiter_count})\n\n")
        text += "(В скобках статистика за смену с 00:00 до 23:59)"
        await bot.edit_message_text(chat_id=admin_id,
                                    message_id=call.message.message_id,
                                    text=text,
                                    reply_markup=InlineKeyboardMarkup().row(
                                        InlineKeyboardButton(text="Назад", callback_data="back_to_admin_menu")))
    except Exception as e:
        print(e)


@dp.callback_query_handler(lambda call: call.data == "admin_commercial")
async def admin_commercial(call: types.CallbackQuery):
    try:
        admin_id = call.from_user.id
        rest = db.get_admin_rest(admin_id)
        total_click_count, current_click_count, total_guests_count, current_guests_count = af.total_and_current_counter(rest)
        text = (f"Статистика вовлеченности пользователей к заведению:\n\n"
                f"Кликабельность заведения через поиск: {total_click_count} ({current_click_count})\n\n"
                f"Обслужено гостей через f2m: {total_guests_count} ({current_guests_count})\n"
                "(В скобках статистика за смену с 00:00 до 23:59)")

        await bot.edit_message_text(chat_id=admin_id,
                                    message_id=call.message.message_id,
                                    text=text,
                                    reply_markup=InlineKeyboardMarkup().row(
                                        InlineKeyboardButton(text="Назад", callback_data="back_to_admin_menu")))
    except Exception as e:
        print(e)


@dp.callback_query_handler(lambda call: call.data == "admin_stop_list")
async def admin_stop_list(call: types.CallbackQuery):
    admin_id = call.from_user.id
    rest = db.get_admin_rest(admin_id)
    if not db.check_stop_list_exists(rest):
        db.create_stop_list(rest)
    await sl.set_stop_list(admin_id, "admin", call.message.message_id)


@dp.callback_query_handler(lambda call: call.data == "back_to_admin_menu")
async def back_to_boss_menu(call: types.CallbackQuery):
    await generate_admin_menu(call.from_user.id, message_id=call.message.message_id)


@dp.callback_query_handler(lambda call: call.data == "admin_reviews")
async def admin_reviews(call: types.CallbackQuery):
    admin_id = call.from_user.id
    await bot.edit_message_text(chat_id=admin_id,
                                message_id=call.message.message_id,
                                text="Отзывы отсутствуют",
                                reply_markup=InlineKeyboardMarkup().row(
                                    InlineKeyboardButton(text="Назад", callback_data="back_to_admin_menu")))


@dp.callback_query_handler(lambda call: call.data == "admin_notification")
async def admin_notification(call: types.CallbackQuery):
    admin_id = call.from_user.id
    message_obj = await bot.send_message(
        chat_id=admin_id,
        text="Отправьте рассылаемое сообщение в этот чат, после чего выберите режим оповещения",
    )
    db.set_users_mode(admin_id, message_obj.message_id, 'notification')

