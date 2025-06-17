# price_list.py

import json

def load_price_list(path="prices.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def format_price_list():
    price_data = load_price_list()
    return "\n".join([f"- {item['title']}: {item['price']}" for item in price_data])
