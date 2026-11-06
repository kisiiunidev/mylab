import requests

TOKEN = "8661589029:AAEohjFF8U0NBpthl3Hu1VHk4hIH3-7bPrs"
CHAT_ID = "8279052184"
message = "Hello using the requests library!"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Message sent successfully!")
else:
    print(f"Failed to send message: {response.text}")
