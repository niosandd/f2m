from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from main import dp, bot, db, config, Tools

def total_and_current_counter(rest):
    stats = db.get_waiters_names_and_stats(rest)
    current_click_count = db.get_current_click_count(rest)
    current_guests_count = db.current_guests_count(rest)
    total_guests_count = db.get_total_guests_count(rest)
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
