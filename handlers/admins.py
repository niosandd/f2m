from datetime import datetime
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

from main import dp, bot, db
import handlers.stop_lists as sl
import handlers.auxiliary_functions as af


temp_review = -1

async def generate_admin_menu(admin_id, rest=None, message_id=None):
    mode = db.get_users_mode(admin_id)
    if not db.check_admin_exists(admin_id):
        db.add_admin(admin_id, rest)
    elif rest:
        db.set_admin_rest(admin_id, rest)
    text = "Какая информация вас интересует: "
    if message_id or mode['key'] == 'admin_mode':
        if mode['key'] == 'admin_mode':
            message_obj = await bot.edit_message_text(chat_id=admin_id,
                                                      message_id=mode['id'],
                                                      text=text,
                                                      reply_markup=admin_menu())
        else:
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
    btn6 = InlineKeyboardButton(text='ВЕРНУТЬСЯ НА ГЛАВНУЮ', callback_data='return_to_choice_of_restaurant')
    menu.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return menu


@dp.callback_query_handler(lambda call: call.data == "admin_waiters_stat")
async def admin_waiters_stat(call: types.CallbackQuery):
    try:
        admin_id = call.from_user.id
        rest = db.get_admin_rest(admin_id)
        stats = db.get_waiters_names_and_stats(rest)
        text = "Общая статистика по официантам:\n\n"
        for waiter in stats:
            if None not in waiter:
                current_waiter_count = db.get_current_waiter_guests(rest, waiter[0])
                text += (
                    f"{waiter[1]} {waiter[2]} {waiter[3]}\nКоличество уникальных заказов: {len(set(eval(waiter[4])))} "
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
        total_click_count, current_click_count, total_guests_count, current_guests_count = af.total_and_current_counter(
            rest)
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
async def back_to_admin_menu(call: types.CallbackQuery):
    await generate_admin_menu(call.from_user.id, message_id=call.message.message_id)


@dp.callback_query_handler(text_contains="go_to")
async def go_to_review(call: types.CallbackQuery):
    global temp_review
    admin_id = call.from_user.id
    rest_name = db.get_admin_rest(admin_id).split(":")[0]
    reviews = db.get_reviews(rest_name)
    if 'next' in call.data:
        temp_review -= 1
    else:
        temp_review += 1
    text = ""
    review = reviews[temp_review]
    if review[0] and review[0] != "None" and review[1] and review[1] != "None":
        text += f"📅 <b>**</b>Дата и время:<b>**</b>   {review[0].split()[1]}  {format_date(review[0].split()[0])}\n"
        text += f"🍽️ <b>**</b>Блюдо:<b>**</b>   {review[1]}\n"
        if review[2] and review[2] != "None":
            rating_stars = "⭐" * review[2]
            text += f"🌟 <b>**</b>Оценка:<b>**</b>   {rating_stars} ({review[2]}/5)\n"
        if review[3] and review[3] != "None":
            text += f"💬 <b>**</b>Мнение:<b>**</b>   \"{review[3]}\"\n\n"
    if temp_review == 0:
        await bot.edit_message_text(chat_id=admin_id,
                                message_id=call.message.message_id,
                                text=text,
                                reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text="Предыдущий отзыв",
                                                                                             callback_data="go_to_last_review"),
                                                                        InlineKeyboardButton(text="Назад",
                                                                                             callback_data="back_to_admin_menu")))
    elif 1 <= temp_review < len(reviews) - 1:
        await bot.edit_message_text(chat_id=admin_id,
                                    message_id=call.message.message_id,
                                    text=text,
                                    reply_markup=InlineKeyboardMarkup().row(
                                        InlineKeyboardButton(text="Предыдущий отзыв",
                                                             callback_data="go_to_last_review"),
                                        InlineKeyboardButton(text="Следующий отзыв",
                                                             callback_data="go_to_next_review"),
                                        InlineKeyboardButton(text="Назад",
                                                             callback_data="back_to_admin_menu")))
    else:
        await bot.edit_message_text(chat_id=admin_id,
                                    message_id=call.message.message_id,
                                    text=text,
                                    reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text="Следующий отзыв",
                                                             callback_data="go_to_next_review"),
                                        InlineKeyboardButton(text="Назад",
                                                             callback_data="back_to_admin_menu")))



@dp.callback_query_handler(lambda call: call.data == "next_review")
async def back_to_admin_menu(call: types.CallbackQuery):
    await bot.edit_message_text()

def format_date(date_str):
    months = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
        7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
    }
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    day = date_obj.day
    month = months[date_obj.month]
    year = date_obj.year
    return f"{day} {month} {year} годa"

@dp.callback_query_handler(lambda call: call.data == "admin_reviews")
async def admin_reviews(call: types.CallbackQuery):
    global temp_review
    admin_id = call.from_user.id
    rest_name = db.get_admin_rest(admin_id).split(":")[0]
    reviews = db.get_reviews(rest_name)
    temp_review = len(reviews) - 1
    if reviews:
        text = ""
        review = reviews[temp_review]
        if review[0] and review[0] != "None" and review[1] and review[1] != "None":
            text += f"📅 <b>**</b>Дата и время:<b>**</b>   {review[0].split()[1]}  {format_date(review[0].split()[0])}\n"
            text += f"🍽️ <b>**</b>Блюдо:<b>**</b>   {review[1]}\n"
            if review[2] and review[2] != "None":
                rating_stars = "⭐" * review[2]
                text += f"🌟 <b>**</b>Оценка:<b>**</b>   {rating_stars} ({review[2]}/5)\n"
            if review[3] and review[3] != "None":
                text += f"💬 <b>**</b>Мнение:<b>**</b>   \"{review[3]}\"\n\n"
    else:
        text = "Отзывы отсутствуют"
    if len(reviews) > 1:
        await bot.edit_message_text(chat_id=admin_id,
                                message_id=call.message.message_id,
                                text=text,
                                reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text="Следующий отзыв",
                                                                                             callback_data="go_to_next_review"),
                                    InlineKeyboardButton(text="Назад", callback_data="back_to_admin_menu")))
    else:
        await bot.edit_message_text(chat_id=admin_id,
                                    message_id=call.message.message_id,
                                    text=text,
                                    reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text="Назад",
                                                                                                 callback_data="back_to_admin_menu")))

@dp.callback_query_handler(lambda call: call.data == "admin_notification")
async def admin_notification(call: types.CallbackQuery):
    admin_id = call.from_user.id
    message_obj = await bot.send_message(
        chat_id=admin_id,
        text="Отправьте рассылаемое сообщение в этот чат, после чего выберите режим оповещения",
    )
    db.set_users_mode(admin_id, message_obj.message_id, 'notification')


@dp.callback_query_handler(lambda call: call.data == 'return_to_choice_of_restaurant')
async def return_to_choice_of_restaurant(call: types.CallbackQuery):
    admin_id = call.from_user.id
    message_obj = await bot.edit_message_text(chat_id=admin_id,
                                message_id=call.message.message_id,
                                text='Выберите заведение:',
                                reply_markup=InlineKeyboardMarkup().add(
                                    InlineKeyboardButton(text="🔎 Поиск кафе", switch_inline_query_current_chat='')))
    db.set_users_mode(admin_id, message_obj.message_id, 'admin_mode')
