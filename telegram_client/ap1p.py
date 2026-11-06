from telegram.ext import Updater, CommandHandler

class CustomUpdater:
    def __init__(self, token):
        self.updater = Updater(token=token)

def main():
    updater = CustomUpdater(token='8661589029:AAEohjFF8U0NBpthl3Hu1VHk4hIH3-7bPrs')
    updater.dispatcher.add_handler(CommandHandler("start", start))

def start(update, context):
    update.message.reply_text("Hello, world!")

if __name__ == '__main__':
    main()
