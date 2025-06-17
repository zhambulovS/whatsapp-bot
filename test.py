# test_twilio.py
from twilio.rest import Client

account_sid = 'ACed697e9e934bb4b67dbfa899f28a112b'
auth_token = '5a04696a2e138074e96be7aeb33aeec9'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  body='Сәлем! Бұл тесттік хабарлама 🚀',
  to='whatsapp:+77762760546'
)

print("Жіберілді:", message.sid)
