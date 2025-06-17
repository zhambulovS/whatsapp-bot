# prompts.py

from studio_info import STUDIO_INFO
from price_list import format_price_list  # JSON-тен прайстарды оқиды

def build_prompt(intent, history, incoming_msg):
    base = f"{STUDIO_INFO}\n\n"

    if intent == "price":
        prices = format_price_list()
        return f"""{base}
Төменде студиямыздың негізгі бағалары берілген:

{prices}

Клиент баға сұрап жатыр. Жылы әрі нақты жауап бер. Қажет болса, қосымша сұрақ қоюға шақыр.

Диалог:
{history}
Клиент: {incoming_msg}
u1atsyzbala:"""

    elif intent == "booking":
        instruction = "Клиент жазылу туралы сұрап жатыр. Қалай брондау керектігін түсіндір."
    elif intent == "location":
        instruction = "Клиент локацияны сұрап отыр. Студия адресін нақты және сыпайы жеткіз."
    elif intent == "services":
        instruction = "Клиент студия қызметтері жайлы білгісі келеді. Қысқа әрі қызықты түсіндір. Сұрақ қою арқылы сатып алуға мәжбұрле."
    else:
        instruction = "Клиентпен жылы, сыпайы тілде жалпы диалог жүргіз. Не қызықтыратының сұра."

    return f"""{base}
Сен Rakurs Production фотостудиясының кәсіби сату маманысын. {instruction}

Диалог:
{history}
Клиент: {incoming_msg}
u1atsyzbala:"""
