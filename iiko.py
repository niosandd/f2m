import requests

import xmltodict
import json


xml_data = ''
def xml_to_dict(element):
    if len(element) == 0:
        return element.text
    return {child.tag: xml_to_dict(child) for child in element}



BASE_URL = "https://api-ru.iiko.services"
BAZA = "https://148-351-449.iiko.it:443"


def get_iiko_menu(api_key, organization_id):
    print(organization_id)
    menu_url = f"https://148-351-449.iiko.it:443/resto/api/products?key={organization_id}"
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
    json_data = json.dumps(xmltodict.parse(menu_data), indent=4, ensure_ascii=False)
    print(json_data)
