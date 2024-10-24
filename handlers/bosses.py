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


def boss_menu():
    menu = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="СТОП-ЛИСТ", callback_data="boss_stop_list")
    btn2 = InlineKeyboardButton(text="ОФИЦИАНТЫ", callback_data="boss_waiters_stat")
    btn3 = InlineKeyboardButton(text="РЕКЛАМА", callback_data="boss_commercial")
    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)
    return menu


@dp.callback_query_handler(lambda call: call.data == "boss_waiters_stat")
async def boss_waiters_stat(call: types.CallbackQuery):
    try:
        boss_id = call.from_user.id
        rest = db.get_boss_rest(boss_id)
        stats = db.get_waiters_names_and_stats()
        text = "Общая статистика по официантам:\n\n"
        for waiter in stats:
            text += f"{waiter[1]} {waiter[2]} {waiter[3]}\nКоличество уникальных заказов: {len(set(eval(waiter[4])))}\n\n"
        await bot.edit_message_text(chat_id=boss_id,
                                    message_id=call.message.message_id,
                                    text=text,
                                    reply_markup=InlineKeyboardMarkup().row(
                                        InlineKeyboardButton(text="Назад", callback_data="back_to_boss_menu")))
    except Exception as e:
        print(e)


@dp.callback_query_handler(lambda call: call.data == "boss_stop_list")
async def boss_stop_list(call: types.CallbackQuery):
    boss_id = call.from_user.id
    rest = db.get_boss_rest(boss_id)
    if not db.check_stop_list_exists(rest):
        db.create_stop_list(rest)
    await set_stop_list(boss_id, call.message.message_id)


def stop_list_status():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="+", switch_inline_query_current_chat='')
    btn2 = InlineKeyboardButton(text="-", callback_data="d_from_stop_list")
    btn3 = InlineKeyboardButton(text="Назад", callback_data="back_to_boss_menu")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup


async def dish_added(boss_id, dish_id):
    rest = db.get_boss_rest(boss_id)
    dish = db.restaurants_get_by_id(dish_id)[4]
    mode = db.get_users_mode(boss_id)
    try:
        stop_list = eval(db.get_stop_list(rest))
    except Exception as e:
        print("stop_list error", e)
        stop_list = {}
    stop_list[dish] = dish_id
    db.set_stop_list(rest, str(stop_list))
    await set_stop_list(boss_id, message_id=mode['id'])


@dp.callback_query_handler(text_contains=f"d_from_stop_list")
async def d_from_stop_list(call: types.CallbackQuery):
    boss_id = call.from_user.id
    rest = db.get_boss_rest(boss_id)
    data = call.data.split('_')
    try:
        stop_list = eval(db.get_stop_list(rest))
    except Exception as e:
        print("stop_list error", e)
        stop_list = {}
    if len(data) > 4:
        dish_id = data[-1]
        dish = db.restaurants_get_by_id(dish_id)[4]
        try:
            stop_list.pop(dish, None)
            db.set_stop_list(rest, str(stop_list))
        except ValueError:
            pass
    await bot.edit_message_text(chat_id=boss_id,
                                message_id=call.message.message_id,
                                text="Нажмите на позицию чтобы удалить",
                                reply_markup=change_stop_list(stop_list))


def change_stop_list(stop_list):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for dish in stop_list:
        btn = InlineKeyboardButton(text=str(dish),
                                   callback_data=f"d_from_stop_list_{stop_list[dish]}")
        keyboard.row(btn)
    btn1 = InlineKeyboardButton(text="Назад", callback_data="back_to_stop_list")
    keyboard.row(btn1)
    return keyboard


@dp.callback_query_handler(lambda call: call.data == "back_to_stop_list")
async def back_to_order(call: types.CallbackQuery):
    await set_stop_list(call.from_user.id, message_id=call.message.message_id)


async def set_stop_list(boss_id, message_id=None):
    try:
        stop_list = list(eval(db.get_stop_list(db.get_boss_rest(boss_id))).keys())
        stop_list_text = ""
        for i in range(len(stop_list)):
            stop_list_text += ind_to_number(i + 1) + " " + stop_list[i] + "\n"
        text = f'\n<b>Сейчас в стоп-листе:</b>' \
               f'\n\n' \
               f'{stop_list_text}'
        if message_id:
            message_obj = await bot.edit_message_text(chat_id=boss_id,
                                                      message_id=message_id,
                                                      text=text,
                                                      reply_markup=stop_list_status())
        else:
            message_obj = await bot.send_message(chat_id=boss_id, text=text, reply_markup=stop_list_status())
        db.set_users_mode(boss_id, message_obj.message_id, 'set_stop_list')
    except Exception as e:
        print(e)


@dp.callback_query_handler(lambda call: call.data == "back_to_boss_menu")
async def back_to_boss_menu(call: types.CallbackQuery):
    await generate_boss_menu(call.from_user.id, call.message.message_id)


async def generate_boss_menu(boss_id, message_id=None):
    text = ("Привет!\n\n"
            f"Это панель управления для менеджера заведения {db.get_boss_rest(boss_id)}\n\n"
            "/СТОП-ЛИСТ - добавление блюд в стоп-лист\n\n"
            "/ОФИЦИАНТЫ - статистика по работе официантов\n\n"
            "/РЕКЛАМА - статистика вовлеченности пользователей")
    if message_id:
        message_obj = await bot.edit_message_text(chat_id=boss_id,
                                                  message_id=message_id,
                                                  text=text,
                                                  reply_markup=boss_menu())
    else:
        message_obj = await bot.send_message(
            chat_id=boss_id,
            text=text,
            reply_markup=boss_menu()
        )
    db.set_users_mode(boss_id, message_obj.message_id, 'boss_menu')
