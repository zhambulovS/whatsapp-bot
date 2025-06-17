# utils.py

import requests
import os

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

def send_whatsapp_message(to, body):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    data = {
        "From": TWILIO_WHATSAPP_NUMBER,
        "To": to,
        "Body": body
    }
    auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    response = requests.post(url, data=data, auth=auth)
    if response.status_code != 201:
        print("❌ WhatsApp жіберу қатесі:", response.status_code, response.text)
    else:
        print("✅ WhatsApp хабарлама жіберілді!")
