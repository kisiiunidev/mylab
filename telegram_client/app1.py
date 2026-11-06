import asyncio
import telegram

# Replace these with your actual token and chat ID
TOKEN = "8661589029:AAEohjFF8U0NBpthl3Hu1VHk4hIH3-7bPrs"
CHAT_ID = "8279052184"

async def send_message():
    bot = telegram.Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="Hello from my Python script! 🚀")

if __name__ == "__main__":
    asyncio.run(send_message())
