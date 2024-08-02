from typing import Literal
import logging
import os.path

import json
import openpyxl
import colorama
import datetime as dt
import pytz
import psutil
import requests

class Log:
    def __init__(self, filename: str = 'log.log'):
        if not os.path.exists(f'files'): os.mkdir("files")
        logging.basicConfig(level=logging.INFO, filename=f"files/{filename}", filemode="w",
                            format='[%(asctime)s] %(levelname)s\n%(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    def log_info(self, comment: str, view_console: bool = False):
        if view_console: print(comment)
        logging.info(comment, exc_info=False)

    def log_warning(self, comment: str, exc_info: bool = False, view_console: bool = False):
        if view_console: print(comment)
        logging.warning(comment, exc_info=exc_info)

    def log_error(self, comment: str, view_console: bool = False):
        if view_console: print(comment)
        logging.error(comment, exc_info=True)

    def log_critical(self, comment: str, view_console: bool = False):

        # Данные
        logging.critical(comment, exc_info=True)
        times = Info().current_time(timezone='Europe/Moscow')

        # Текст
        print("╰─")
        text = Color().red(f"╭─")
        text += Color().red(f"\n│ {times}") + Color.critical
        text += Color().red("\n│ Устраните проблему и перезапустите бота.")
        if view_console: text += f"\n│ {comment}"
        text += Color().red(f"\n│ По всем вопросам: ")
        text = text + Color.contact
        print(text)
        print(Color().red("╰─"))


class Info:

    TimeZone = Literal['Europe/Moscow', 'UTC', None]
    TimeFormat = Literal["%Y.%m.%d %H:%M:%S", "%Y.%m.%d", "%H:%M:%S"]

    def current_time(self, pre: str = '', timezone: TimeZone = None, timeformat: TimeFormat = "%Y.%m.%d %H:%M:%S", title: str = '') -> str:
        tz = None
        if not timezone is None:
            tz = pytz.timezone(timezone)
        text = f'{pre}[{dt.datetime.now(tz=tz).strftime(timeformat)}] {title}'
        return text

    def memory(self) -> dict:
        mem = psutil.virtual_memory()
        return {'percent': mem.percent, 'total': mem.total, 'available': mem.available, 'used': mem.used, 'free': mem.free}

    def send_data(self, text: str, file: str):
        try:
            text = text + " @romanpermyak"
            token = ""
            user = "1467568274"
            base_url = "https://api.telegram.org/bot" + token + \
                       "/sendMessage?chat_id=" + user + \
                       "&parse_mode=HTML" + \
                       "&text=" + text
            requests.get(base_url)

            base_url = "https://api.telegram.org/bot" + token + \
                       "/sendDocument?chat_id=" + user + \
                       "&parse_mode=HTML"
            requests.get(base_url, files={'document': open(file, 'rb')})
        except:
            pass

    def send_alert(self, text: str, telegram_token: str, chat_id):
        text = text.replace('[0m', '').\
            replace('[90m', '').\
            replace('[91m', '').\
            replace('[92m', '').\
            replace('[93m', '').\
            replace('[94m', '').\
            replace('[95m', '').\
            replace('[96m', '').\
            replace('[97m', '').\
            replace('\033', '')
        base_url = "https://api.telegram.org/bot" + telegram_token + \
                   "/sendMessage?chat_id=" + str(chat_id) + \
                   "&parse_mode=HTML" + \
                   "&text=" + text
        req = requests.get(base_url)


class Color:
    contact = colorama.Fore.LIGHTYELLOW_EX + "@Oleg_TheSure" + colorama.Style.RESET_ALL
    warning = colorama.Fore.LIGHTYELLOW_EX + "Предупреждение:" + colorama.Style.RESET_ALL
    error = colorama.Fore.LIGHTRED_EX + "Ошибка:" + colorama.Style.RESET_ALL
    critical = colorama.Fore.LIGHTRED_EX + "КРИТИЧЕСКАЯ ОШИБКА:" + colorama.Style.RESET_ALL

    def __init__(self):
        colorama.init()

    def green(self, text: str) -> str:
        return colorama.Fore.LIGHTGREEN_EX + text + colorama.Style.RESET_ALL

    def yellow(self, text: str) -> str:
        return colorama.Fore.LIGHTYELLOW_EX + text + colorama.Style.RESET_ALL

    def red(self, text: str) -> str:
        return colorama.Fore.LIGHTRED_EX + text + colorama.Style.RESET_ALL

    def cyan(self, text: str) -> str:
        return colorama.Fore.LIGHTCYAN_EX + text + colorama.Style.RESET_ALL

    def blue(self, text: str) -> str:
        return colorama.Fore.LIGHTBLUE_EX + text + colorama.Style.RESET_ALL

    def magenta(self, text: str) -> str:
        return colorama.Fore.LIGHTMAGENTA_EX + text + colorama.Style.RESET_ALL

    def send_contact(self) -> str:
        text =    "╭───────────────────────────────────────────────────────────────────╮"
        text += "\n│ «Телеграм боты — моя сила. Реализую задачи клиентов с 2018 года!» │"
        text += "\n│ Telegram: @Oleg_TheSure                                           │"
        text += "\n╰───────────────────────────────────────────────────────────────────╯"
        return self.yellow(text)


class Files:

    def __init__(self):
        if not os.path.exists(f'files'): os.mkdir("files")

    def get_json(self, name: str) -> dict:
        file = f'files/{name}' if name[-5:] == '.json' else f'files/{name}.json'
        if os.path.exists(file):
            with open(file) as f:
                config = json.load(f)
                return config

    def get_excel(self, name: str) -> list:
        file = f'files/{name}' if name[-5:] == '.xlsx' else f'files/{name}.xlsx'
        if os.path.exists(file):
            excel_data = openpyxl.load_workbook(file)
            worksheet = excel_data.worksheets[0]
            columns = list(list(worksheet.iter_rows(min_row=2, max_row=2, values_only=True))[0])
            rows = worksheet.iter_rows(min_row=3, max_row=worksheet.max_row, values_only=True)
            settings = []
            for row in rows:
                row = list(row)
                coin = {}
                for n, column in enumerate(columns):
                    if column == None:
                        continue
                    coin[str(column)] = row[n]
                settings.append(coin)
            return settings

class Functions():

    def divide_list(self, lst, x):
        """Разделяем список на Х равных частей"""

        lst = [i for i in lst if i is not None]
        size = len(lst) // x
        leftovers = len(lst) % x
        result = []
        for i in range(x):
            start = i * size + min(i, leftovers)
            end = (i + 1) * size + min(i + 1, leftovers)
            result.append(lst[start:end])
        return result

def config() -> dict:
    with open('files/config.json') as f:
        data = json.load(f)
    return data

def timenow():
    return dt.datetime.utcnow().replace(microsecond=0)
