from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

from main import dp, bot, db, config, Tools
import handlers.stop_lists as sl

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


@dp.callback_query_handler(lambda call: call.data == "admin_notification")
async def admin_notification(call: types.CallbackQuery):
    admin_id = call.from_user.id
    message_obj = await bot.send_message(
        chat_id=admin_id,
        text="Отправьте рассылаемое сообщение в этот чат, после чего выберите режим оповещения",
    )
    db.set_users_mode(user, message_obj.message_id, 'notification')
