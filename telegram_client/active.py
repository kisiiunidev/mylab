import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Enable logging to see errors and console output
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = "8813259005:AAEnvK9ClkSYXhxLSgtDiehX1euG7AHp_DQ"

# Handler for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Hi {user_name}! I'm online. Send me a message and I'll respond.")

# Handler for regular text messages (Chat / Respond)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_name = update.effective_user.first_name
    
    # Custom logic or simple echo response
    response_text = f"Received your message, {user_name}: \"{user_text}\""
    
    # Send the response back to the user
    await update.message.reply_text(response_text)

if __name__ == "__main__":
    # Build the application with your bot token
    application = ApplicationBuilder().token(TOKEN).build()

    # Register command handler
    application.add_handler(CommandHandler("start", start))

    # Register message handler (listens to all text messages except commands)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Start polling for incoming messages
    print("Bot is polling for messages... Press Ctrl+C to stop.")
    application.run_polling()
