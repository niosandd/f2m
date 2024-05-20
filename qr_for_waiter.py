import pyqrcode
import telebot
import png


async def make_qrcode(dish):
    url = f"https://t.me/food2mood_bot?start=order:{dish}"
    qrcode = pyqrcode.create(url)
    qrcode.png('QR CODE.png', scale=6)
    with open('QR CODE.png', made='rb') as file:
        bot.send_photo(message.chat.id, photo=file)
