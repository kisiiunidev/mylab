import os
import logging
from dotenv import load_dotenv
from flask import Flask
from models import db, User, Message
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Initialize Flask app configuration for SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///bot_database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Hi {user_name}! I'm your chat assistant with full database history. Let's talk!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    from_user = update.effective_user
    
    tg_user_id = from_user.id
    username = from_user.username
    first_name = from_user.first_name

    with app.app_context():
        # 1. Find or create user
        user = User.query.filter_by(telegram_id=tg_user_id).first()
        if not user:
            user = User(telegram_id=tg_user_id, username=username, first_name=first_name)
            db.session.add(user)
            db.session.commit()
        
        # 2. Save incoming user message
        incoming = Message(chat_id=chat_id, text=user_text, sender="user", user_id=user.id)
        db.session.add(incoming)
        db.session.commit()

        # 3. Retrieve recent chat history for this chat (e.g., last 10 messages)
        recent_messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp.desc()).limit(10).all()
        recent_messages.reverse() # Put them in chronological order

        # Build chat history summary or context list
        chat_history_summary = []
        for msg in recent_messages:
            sender_label = "User" if msg.sender == "user" else "Bot"
            chat_history_summary.append(f"{sender_label}: {msg.text}")

        # 4. Generate your response using the chat history context
        # (Here you can also pass `chat_history_summary` to an LLM like OpenAI if you want AI conversational responses)
        total_exchanges = len(recent_messages)
        reply_text = f"[{total_exchanges} messages in history]\nBot response to: \"{user_text}\""

        # 5. Save outgoing bot message
        outgoing = Message(chat_id=chat_id, text=reply_text, sender="bot", user_id=user.id)
        db.session.add(outgoing)
        db.session.commit()

    await update.message.reply_text(reply_text)

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Complete chat bot is polling... Press Ctrl+C to stop.")
    application.run_polling()
