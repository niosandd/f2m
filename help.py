import time
import db
import json
from typing import Union
from typing import Union

"""
Работа с JSON файлом.
"""

def edit_json_value(name: Union[str, list], val: Union[float, str]) -> None:
    with open('files/config.json') as f:
        data = json.load(f)

    if type(name) == str:
        data[name] = val
    else:
        data[name[0]][name[1]] = val

    with open('files/config.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_row(usdt: float, tp: float, symbol: str = None) -> None:
    if symbol is None:
        data = json.loads(db.config_get_rows())
    else:
        data = json.loads(db.reports_get_rows(symbol))

    names = list(data.keys())
    for i in range(100):
        name = f"row_{i+1}"
        if name not in names:
            data[name] = {
                'usdt': usdt,
                'tp': tp
            }
            break

    if symbol is None:
        db.config_set_rows(json.dumps(data))
    else:
        db.reports_set_rows(symbol, json.dumps(data))

def get_row(numb: Union[int, None] = None, symbol: Union[str, None] = None) -> Union[dict, None]:
    if symbol is None:
        data = json.loads(db.config_get_rows())
    else:
        data = json.loads(db.reports_get_rows(symbol))

    result = None
    if numb is not None:
        name = f"row_{numb}"
        if name in data:
            result = data[name]

    return result

def get_rows(symbol: str = None) -> str:
    if symbol is None:
        data = json.loads(db.config_get_rows())
    else:
        data = json.loads(db.reports_get_rows(symbol))

    texts = ''
    for name in data:
        if 'row' in name:
            text = f"• Переоткрытие {str(name)[4:]}:  <code>{data[name]['usdt']}$ - {data[name]['tp']}%</code>"
            texts += f"{text}\n"

    return texts

def del_row(symbol: str = None) -> None:
    if symbol is None:
        data = json.loads(db.config_get_rows())
    else:
        data = json.loads(db.reports_get_rows(symbol))

    names = list(data.keys())
    for i in range(100, 0, -1):
        name = f"row_{i}"
        if name in names:
            del data[name]
            break

    if symbol is None:
        db.config_set_rows(json.dumps(data))
    else:
        db.reports_set_rows(symbol, json.dumps(data))

def config() -> dict:
    with open('files/config.json') as f:
        data = json.load(f)
    return data