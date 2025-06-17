import os
import requests
import sqlite3
from flask import Flask, request
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
from intent import detect_intent
from prompts import build_prompt
from utils import send_whatsapp_message

GREETING_TEXT = "Сәлеметсіз бе! Rakurs Production студиясына қош келдіңіз 🌸 Біз Love Story фотосессияларын студия ішінде ұсынамыз. Қандай сұрағыңыз бар еді?"

# .env файлын жүктеу
load_dotenv()

# Flask серверін бастау
app = Flask(__name__)

# OpenAI клиенті
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Twilio параметрлері
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
ADMIN_WHATSAPP_NUMBER = os.getenv('ADMIN_WHATSAPP_NUMBER')
# Қате болса тоқтату
required_vars = [client.api_key, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER]
if not all(required_vars):
    raise Exception("❌ .env ішінде бір немесе бірнеше API кілт жетіспейді!")

# SQLite жады базасы
conn = sqlite3.connect("memory.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS memory (
        user TEXT,
        sender TEXT,
        message TEXT
    )
''')
conn.commit()

# Амандасуды тексеру функциясы
def has_greeted(user):
    c.execute("SELECT message FROM memory WHERE user = ? AND sender = 'bot' ORDER BY rowid DESC LIMIT 5", (user,))
    last_msgs = [msg[0].lower() for msg in c.fetchall()]
    greetings = ["сәлем", "әлеумет", "сәлеметсіз бе", "қайырлы"]
    return any(any(greet in msg for greet in greetings) for msg in last_msgs)

# Соңғы хабарламаларды диалог ретінде алу
def get_chat_history(user, limit=50):
    c.execute(
        "SELECT sender, message FROM memory WHERE user = ? ORDER BY rowid DESC LIMIT ?",
        (user, limit)
    )
    rows = reversed(c.fetchall())
    history = "\n".join(
        [f"{'Клиент' if sender == 'user' else 'u1atsyzbala'}: {msg}" for sender, msg in rows]
    )
    return history

# WhatsApp хабарлама жіберу функциясы
# def send_whatsapp_message(to, body):
#     url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
#     data = {
#         "From": TWILIO_WHATSAPP_NUMBER,
#         "To": to,
#         "Body": body
#     }
#     auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#     response = requests.post(url, data=data, auth=auth)
#     if response.status_code != 201:
#         print("❌ WhatsApp жіберу қатесі:", response.status_code, response.text)
#     else:
#         print("✅ WhatsApp хабарлама жіберілді!")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # send_whatsapp_message("whatsapp:+77762760546", "Тест на мой номер")
        incoming_msg = request.form.get("Body")
        from_number = request.form.get("From")

        print("📩 Хабарлама:", incoming_msg)
        print("📱 Кімнен:", from_number)

        if not incoming_msg or not from_number:
            print("⚠️ Хабарлама немесе номер бос!")
            return "Missing message or sender", 10000

        # Чат тарихын тазалау командасы
        if incoming_msg.strip().lower() == "!тазалау":
            c.execute("DELETE FROM memory WHERE user = ?", (from_number,))
            conn.commit()
            send_whatsapp_message(from_number, "✅ Чат тарихы сәтті тазаланды!")
            return str(MessagingResponse())

        # Егер әлі амандаспаған болса — амандасу
        if not has_greeted(from_number):
            greeting = "Сәлеметсіз бе! Rakurs Production фотостудиясына хабарласқаныңызға рахмет. Біз сізге міндетті түрде жауап береміз.😊"
            send_whatsapp_message(from_number, greeting)
            c.execute("INSERT INTO memory (user, sender, message) VALUES (?, ?, ?)", (from_number, 'bot', greeting))
            conn.commit()
            return str(MessagingResponse())

        # Диалогты контекст ретінде дайындау
        history = get_chat_history(from_number)
        prompt = f"""
Сен — "Rakurs Production" фотостудиясының жылы жүзді, сату фокусындағы кәсіби менеджерсің. "Love Story" видео фотосессияларын сатумен айналысасың. Клиентпен WhatsApp арқылы сөйлесіп отырсың. Міндетің – клиентке нақты ақпарат беріп, оларды сатып алуға мәжбүрлеу.

Студия туралы нақты ақпарат:
- Орналасқан жері: Актөбе, Смагулова 9 мекен-жайында орналаскан
- Бағалары: Love Story фотосессиясы 40 000 теңгеден басталады
- Студия ішінде кәсіби жарық пен заманауи фотоаппараттар бар
- Қызметтер: Love Story фотосессиясы, мерейтойлар, отбасы фотосессиялары

Талаптар:
- Амандасқанда тек бір рет сәлемдес (егер бұрын амандаспаған болса), және осы текст пен амандас "Сәлеметсіз бе! Rakurs Production фотостудиясына хабарласқаныңызға рахмет. Біз сізге міндетті түрде жауап береміз.😊".
- Қайталанба. Клиент не сұрап тұр — соған нақты жауап бер.
- Егер баға, локация, уақыт туралы сұраса — нақтылап айт.
- Қызметіміз туралы қысқаша, бірақ қызықты етіп түсіндір.

Төменде клиентпен нақты диалог:
{history}
Клиент: {incoming_msg}
RakursBot:
"""

        # Ниетті анықтау
        intent = detect_intent(incoming_msg)

        # GPT жауап алу
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.4,
        )
        reply = response.choices[0].message.content.strip()

        # Егер мекен жай туралы сұрақ болса, сілтемені қосу
        address_keywords = ["адрес", "мекен-жай", "орналасқан жер", "қайда орналасқан", "орналасқан"]
        if any(word in incoming_msg.lower() for word in address_keywords):
            gis_link = "https://2gis.kz/almaty/firm/1234567890"  # Өз сілтемеңізді қойыңыз
            if gis_link not in reply:
                reply += f"\n\n📍 Толығырақ мекен-жай мен карта үшін: {gis_link}"

        # Егер ниет - жазылу болса, қосымша хабарлама жіберу
        if intent == "booking":
            try:
                print("🔥 Бронь интенты анықталды!")
                
                # 1. Клиентке растау хабарламасы
                booking_reply = "Жақсы, сізді жазып қоямын! Сізге қандай күн мен сағат ыңғайлы болар екенін айтыңызшы?"
                send_whatsapp_message(from_number, booking_reply)
                
                # 2. Жадыға сақтау
                c.execute("INSERT INTO memory (user, sender, message) VALUES (?, ?, ?)", 
                        (from_number, 'user', incoming_msg))
                c.execute("INSERT INTO memory (user, sender, message) VALUES (?, ?, ?)", 
                        (from_number, 'bot', booking_reply))
                conn.commit()
                
                # 3. Администраторға хабарлама (тест режимінде Sandbox-қа)
                admin_number = ADMIN_WHATSAPP_NUMBER  # админ нөмірі
                booking_info = f"🔥 ЖАҢА БРОНЬ!\nНөмір: {from_number}\nХабарлама: «{incoming_msg}»"
                send_whatsapp_message(admin_number, booking_info)
                
                print("✅ Бронь расталды және хабарламалар жіберілді")
                return str(MessagingResponse())
            
            except Exception as e:
                print(f"❌ Бронь өңдеу кезінде қате: {str(e)}")
                # Қате болған жағдайда кәдімгі жалғастыру

        # GPT жауапқа қосымша сұрақ қою (мысалы, классикалық па, сценарий бойынша ма?)
        if not has_greeted(from_number):
            reply += "\n\n😊 Сізге қандай Love Story қызықты? Классикалық па, әлде сценарий бойынша ма?"

        print("🤖 GPT жауап:", reply)
        send_whatsapp_message(from_number, reply)

        # Жадыға сақтау
        c.execute("INSERT INTO memory (user, sender, message) VALUES (?, ?, ?)", (from_number, 'user', incoming_msg))
        c.execute("INSERT INTO memory (user, sender, message) VALUES (?, ?, ?)", (from_number, 'bot', reply))
        conn.commit()

        resp = MessagingResponse()
        return str(resp)

    except Exception as e:
        print("❌ ҚАТЕ:", e)
        return str(e), 100000


if __name__ == "__main__":
    app.run(debug=True)
