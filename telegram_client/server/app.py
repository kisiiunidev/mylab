import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from models import db, User, Message

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///bot_database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB with app
db.init_app(app)

with app.app_context():
    db.create_all()

def send_telegram_message(chat_id, text):
    """Send a message back via Telegram API."""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    return response.json()

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    """Endpoint that Telegram calls whenever a user sends a message (Webhook approach)."""
    update = request.get_json()
    
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        from_user = msg.get("from", {})
        
        tg_user_id = from_user.get("id")
        username = from_user.get("username")
        first_name = from_user.get("first_name")
        
        with app.app_context():
            # Find or create the user in the database
            user = User.query.filter_by(telegram_id=tg_user_id).first()
            if not user:
                user = User(telegram_id=tg_user_id, username=username, first_name=first_name)
                db.session.add(user)
                db.session.commit()
            
            # Save incoming user message
            incoming_msg = Message(chat_id=chat_id, text=text, sender="user", user_id=user.id)
            db.session.add(incoming_msg)
            
            # Generate your chatbot's response logic
            reply_text = f"Hello {first_name or 'there'}, I saved your message: '{text}' in Flask!"
            
            # Save outgoing bot message
            outgoing_msg = Message(chat_id=chat_id, text=reply_text, sender="bot", user_id=user.id)
            db.session.add(outgoing_msg)
            db.session.commit()
            
            # Send reply to Telegram
            send_telegram_message(chat_id, reply_text)
            
    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def index():
    return "Flask Telegram Bot is running!", 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("FLASK_RUN_PORT", 5000)))
