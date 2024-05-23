import re
from main import dp, bot, db, config, Tools
import difflib
import requests
import json
import random
import pandas as pd

def read_table(restaurant: str, category: str, mood: str, style: str, rec: str,
               blacklist: str, numb: int):
    # Загружаем таблицу с меню
    df = pd.DataFrame(db.restaurants_get(restaurant), columns=[
        'id',
        'Название ресторана',
        'Адрес ресторана',
        'Категория',
        'Название блюда',
        'Описание блюда',
        'Ингредиенты',
        'Стиль питания',
        'Настроение',
        'Рекомендации нутрициолога',
        'Рекомендации сообщества',
        'Рекомендации Обломова',
        'Рекомендации Евлеева',
        'Отзывы',
        'Рейтинг',
        'Картинки',
        'Ссылка'
    ])

    # Выделяем только то меню, что сейчас запрашивает клиент
    '''
        Добавлять новую сортировки при добавлении авторитета в той же
        последовательности, что и в примерах сверху с снизу:
            if rec == 'Обломов' and (df[0][10] != 'None' or df[0][10] is not None):
                rec_n = 10
            if rec == 'Ивлев' and (df[0][11] != 'None' or df[0][11] is not None):
                rec_n = 11
            if ...
    '''
    df = df[df['Настроение'].str.contains(mood)]
    df = df[df['Стиль питания'].str.contains(style)]
    df = df.loc[df['Категория'] == category]
    df = df.values.tolist()
    if not len(df):
        return None, None, None

    rec_mood = {
        'Радость': 0,
        'Печаль': 1,
        'Гнев': 2,
        'Спокойствие': 3,
        'Волнение': 4,
    }

    rec_item = 0
    if rec == 'Нутрициолог' and (df[0][9] != 'None' or df[0][9] != '' or df[0][9] is not None):
        rec_item = 9
    if rec == 'Пользователи' and (df[0][10] != 'None' or df[0][10] != '' or df[0][10] is not None):
        rec_item = 10
    if rec == 'Обломов' and (df[0][11] != 'None' or df[0][11] != '' or df[0][11] is not None):
        rec_item = 11
    if rec == 'Ивлев' and (df[0][12] != 'None' or df[0][12] != '' or df[0][12] is not None):
        rec_item = 12

    if rec_item == 0:
        return None, None, None

    def sort_by(item):
        mood_info = item[rec_item].split(', ')
        min_order = float('inf')
        for info in mood_info:
            match = re.match(r'(\w+)\s*=\s*(\d+)', info)
            if match:
                mood_name, mood_order = match.groups()
                if mood_name.strip() == mood:
                    min_order = min(min_order, int(mood_order))
        return min_order

    # Изменение в сортировке, передача rec_item в sort_by функцию
    df_new = sorted(df, key=lambda x: sort_by(x))

    dishes = []
    for dish in df_new:
        dish_ingredients_unformatted = str(dish[6]).strip().lower()
        dish_ingredients = dish_ingredients_unformatted.split(',')

        # Проверка через AI
        if check_blacklist_with_ai(blacklist, dish_ingredients):
            # print("Пропускаем блюдо из-за запрещенного ингредиента:", dish[4])
            # print("Запрещенные ингредиенты:", blacklist)
            # print("Ингредиенты блюда:", dish_ingredients)
            continue

        # Проверка через difflib
        drop = False
        for ing in blacklist.replace(' ', '').split(','):
            ing = str(ing).lower().strip()
            if ing in dish_ingredients:
                drop = True
                break

        if drop:
            continue

        dishes.append({
            "Ресторан": dish[1],
            "Адрес": dish[2],
            "Категория": dish[3],
            "Название": dish[4],
            "Описание": dish[5],
            "Ингредиенты": dish_ingredients,
            "Стиль питания": dish[7],
            "Настроение": mood,
            "Ссылка": dish[9]
        })

    # Возвращаем результат
    if len(dishes) > 0:
        if len(dishes) > numb:
            return dishes[numb], len(dishes), len(dishes) - numb - 1
        else:
            return dishes[-1], len(dishes), 0
    else:
        return None, None, None


def get_dish(user: int):
    restaurant = db.get_client_temp_rest(user).split(':')
    category = db.get_client_temp_category(user)
    mood = db.get_client_temp_mood(user)
    style = db.get_client_style(user)
    rec = db.get_client_temp_recommendation(user)
    blacklist = db.get_client_blacklist(user)
    numb = db.get_client_temp_dish(user)

    return read_table(restaurant[0], category, mood, style, rec, blacklist, numb)


def check_blacklist_with_ai(blacklist, dish_ingredients):
    # Функция для определения, является ли ингредиент морепродуктом
    def is_seafood(ingredient):
        seafood_keywords = ['креветка', 'краб', 'мидии', 'корюшка', 'лосось', 'тунец', 'осётр', 'икра']
        for keyword in seafood_keywords:
            if keyword in ingredient:
                return True
        return False

    bothubClient = requests.Session()
    token = config()['chatgpt']
    bothubClient.headers.update({'Authorization': f'Bearer {token}'})
    answer = "Нет"  # По умолчанию считаем, что ответ "Нет"

    for ing in blacklist.replace(' ', '').split(','):
        ing = str(ing).lower()
        for ingredient in dish_ingredients:
            # Если ингредиент является морепродуктом, пропускаем его
            if is_seafood(ingredient):
                continue

            # Проверяем соответствие ингредиента чёрному списку
            if difflib.SequenceMatcher(None, ing, ingredient).ratio() >= 0.5:
                base_rule = f"""
                У меня есть запрещенный продукт(ы): «{blacklist}». Они относятся хоть к какому-то ингредиенту в списке: «{ingredient}, {dish_ingredients}»? Нужен только ответ, либо Да, либо Нет. 
                Правило: Также не забывай про словосочетания. Например: Тигровые креветки - это креветка. Омлет состоит из яиц и молока, то есть нельзя яйца и молоко, то есть они тоже являются запрещенными продуктами.
                """
                response = bothubClient.post("https://bothub.chat/api/v1/dev/chat/completion/sync", json={
                    "messages": [],
                    "message": {
                        "role": "user",
                        "content": base_rule
                    },
                    "settings": {
                        "temperature": 0.7,
                        "top_p": 0.5,
                        "model": "gpt-3.5-turbo"
                    }
                })

                # Проверяем, что ответ не пустой
                if response.text:
                    try:
                        answer = response.json()['aiMessage']['content']
                        if answer.lower() == 'да':
                            return True
                    except (KeyError, json.JSONDecodeError) as e:
                        pass
                    # Если в ответе от AI содержится слово "Да", также возвращаем True
                    if "да" in response.text.lower():
                        return True

    return False




def read_table_2(user, mood: str, style: str, blacklist: str):
    # Загружаем таблицу с меню
    df = pd.DataFrame(db.recommendations_get_all(), columns=[
        'id',
        'Название ресторана',
        'Адрес ресторана',
        'Категория',
        'Название блюда',
        'Описание блюда',
        'Ингредиенты',
        'Стиль питания',
        'Настроение',
        'Ссылка'
    ])

    # Выделяем только то меню, что сейчас запрашивает клиент
    df = df[df['Настроение'].str.contains(mood)]
    df = df[df['Стиль питания'].str.contains(style)]

    if df.empty:
        return None, None

    dishes = []
    for dish in df.values.tolist():
        dish_ingredients = [ingredient.strip() for ingredient in str(dish[6]).lower().split(',')]

        if check_blacklist_with_ai(blacklist, dish_ingredients):
            print("Пропускаем блюдо из-за запрещенного ингредиента:", dish[4])
            print("Запрещенные ингредиенты:", blacklist)
            print("Ингредиенты блюда:", dish_ingredients)
            continue

        dishes.append({
            "Ресторан": dish[1],
            "Адрес": dish[2],
            "Категория": dish[3],
            "Название": dish[4],
            "Описание": dish[5],
            "Ингредиенты": dish[6],
            "Стиль питания": dish[7],
            "Настроение": mood,
            "Ссылка": dish[9]
        })

    if dishes:
        dish = random.choice(dishes)
        while True:
            dish_id = db.restaurants_get_dish(
                dish['Ресторан'],
                dish['Адрес'],
                dish['Название']
            )[0]
            if dish_id != db.get_client_temp_dish_id(user):
                break
            dish = random.choice(dishes)
        db.set_client_temp_dish(user, dishes.index(dish))
        return dish, len(dishes)
    else:
        return None, None



def get_recommendation(user: int):
    mood = db.get_client_temp_mood(user)
    style = db.get_client_style(user)
    blacklist = db.get_client_blacklist(user)

    return read_table_2(user, mood, style, blacklist)
