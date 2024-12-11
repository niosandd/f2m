import datetime
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from main import dp, bot, db, config, Tools

def total_and_current_counter(rest):
    stats = db.get_waiters_names_and_stats(rest)
    last_check_time = db.get_last_check_time(rest)
    if last_check_time == datetime.datetime.now().strftime("%Y-%m-%d"):
        current_click_count = db.get_current_click_count(rest)
    else:
        current_click_count = 0
        db.set_current_click_count(rest, current_click_count)
    db.set_last_check_time(rest, datetime.datetime.now().strftime("%Y-%m-%d"))
    current_guests_count = db.get_current_guests_count(rest)
    total_guests_count = 0
    total_click_count = db.get_total_click_count(rest)
    for waiter in stats:
        if None not in waiter:
            total_guests_count += len(set(eval(waiter[4])))
    return total_click_count, current_click_count, total_guests_count, current_guests_count


def ind_to_number(ind):
    numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    result = ""
    for char in str(ind):
        result += numbers[int(char)]
    return result
