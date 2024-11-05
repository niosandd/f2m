from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

from main import dp, bot, db, config, Tools


def ind_to_number(ind):
    numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    result = ""
    for char in str(ind):
        result += numbers[int(char)]
    return result


async def set_stop_list(user_id, actor, message_id=None):
    try:
        stop_list = list(eval(db.get_stop_list(db.get_admin_rest(user_id))).keys())
        stop_list_text = ""
        for i in range(len(stop_list)):
            stop_list_text += ind_to_number(i + 1) + " " + stop_list[i] + "\n"
        text = f'\n<b>Сейчас в стоп-листе:</b>' \
               f'\n\n' \
               f'{stop_list_text}'
        if message_id:
            message_obj = await bot.edit_message_text(chat_id=user_id,
                                                      message_id=message_id,
                                                      text=text,
                                                      reply_markup=stop_list_status(actor))
        else:
            message_obj = await bot.send_message(chat_id=user_id, text=text, reply_markup=stop_list_status(actor))
        db.set_users_mode(user_id, message_obj.message_id, f'set_stop_list_{actor}')
    except Exception as e:
        print(e)


async def dish_added(user_id, actor, dish_id):
    if actor == "admin":
        rest = db.get_admin_rest(user_id)
    else:
        rest = db.get_boss_rest(user_id)
    dish = db.restaurants_get_by_id(dish_id)[4]
    mode = db.get_users_mode(user_id)
    try:
        stop_list = eval(db.get_stop_list(rest))
    except Exception as e:
        print("stop_list error", e)
        stop_list = {}
    stop_list[dish] = dish_id
    db.set_stop_list(rest, str(stop_list))
    await set_stop_list(user_id, actor, message_id=mode['id'])


def stop_list_status(actor):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="+", switch_inline_query_current_chat='')
    if actor == "admin":
        btn2 = InlineKeyboardButton(text="-", callback_data="admin_d_from_stop_list")
        btn3 = InlineKeyboardButton(text="Назад", callback_data="back_to_admin_menu")
    else:
        btn2 = InlineKeyboardButton(text="-", callback_data="boss_d_from_stop_list")
        btn3 = InlineKeyboardButton(text="Назад", callback_data="back_to_boss_menu")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup


@dp.callback_query_handler(text_contains=f"d_from_stop_list")
async def d_from_stop_list(call: types.CallbackQuery):
    user_id = call.from_user.id
    data = call.data.split('_')
    if data[0] == "admin":
        actor = "admin"
        rest = db.get_admin_rest(user_id)
    else:
        actor = "boss"
        rest = db.get_boss_rest(user_id)
    try:
        stop_list = eval(db.get_stop_list(rest))
    except Exception as e:
        print("stop_list error", e)
        stop_list = {}
    if len(data) > 5:
        dish_id = data[-1]
        dish = db.restaurants_get_by_id(dish_id)[4]
        try:
            stop_list.pop(dish, None)
            db.set_stop_list(rest, str(stop_list))
        except ValueError:
            pass
    await bot.edit_message_text(chat_id=user_id,
                                message_id=call.message.message_id,
                                text="Нажмите на позицию чтобы удалить",
                                reply_markup=change_stop_list(stop_list, actor))


def change_stop_list(stop_list, actor):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for dish in stop_list:
        if actor == "admin":
            btn = InlineKeyboardButton(text=str(dish),
                                       callback_data=f"admin_d_from_stop_list_{stop_list[dish]}")
        else:
            btn = InlineKeyboardButton(text=str(dish),
                                       callback_data=f"boss_d_from_stop_list_{stop_list[dish]}")
        keyboard.row(btn)
    if actor == "admin":
        btn1 = InlineKeyboardButton(text="Назад", callback_data="admin_back_to_stop_list")
    else:
        btn1 = InlineKeyboardButton(text="Назад", callback_data="boss_back_to_stop_list")
    keyboard.row(btn1)
    return keyboard


@dp.callback_query_handler(text_contains=f"back_to_stop_list")
async def back_to_stop_list(call: types.CallbackQuery):
    data = call.data.split('_')
    await set_stop_list(call.from_user.id, data[0], message_id=call.message.message_id)
