import requests
import xml.etree.ElementTree as ET


def parse_menu_from_xml(text):
    # Читаем XML-файл
    root = ET.fromstring(text)

    menu = []

    # Проходим по категориям
    for category in root.findall('Category'):
        category_name = category.get('name')  # Название категории
        for item in category.findall('Item'):
            # Достаем данные о блюде
            item_data = {
                'id': item.find('ID').text,
                'name': item.find('productType').text,
                'price': float(item.find('Price').text),
                'description': item.find('Description').text,
                'category': category_name
            }
            menu.append(item_data)

    print(menu)


BASE_URL = "https://api-ru.iiko.services"
BAZA = "https://148-351-449.iiko.it:443"


def get_iiko_menu(api_key, organization_id):
    print(organization_id)
    #menu_url = f"https://148-351-449.iiko.it:443/resto/api/1/nomenclature/{organization_id}"
    menu_url = f"https://148-351-449.iiko.it:443/resto/api/products/dish?key={organization_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(menu_url, headers=headers)

        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        return {"error": f"Ошибка соединения: {str(e)}"}


def get_iiko_organizations(api_key):
    url = f"https://148-351-449.iiko.it:443/resto/api/auth?login=user&pass=a8077481a4001dc56965d738106dd8792ff6991a"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.get(url, headers=headers)
        return response.text
    except requests.RequestException as e:
        return {"error": f"Ошибка соединения: {str(e)}"}


if __name__ == "__main__":
    API_KEY = "f90276d7c54e4cc0bd17e2e332ee3e7f"
    organizations_data = get_iiko_organizations(API_KEY)
    menu_data = get_iiko_menu(API_KEY, organizations_data)
    print(menu_data)
    parse_menu_from_xml(menu_data)
