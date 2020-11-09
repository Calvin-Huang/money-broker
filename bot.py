from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext)

TOKEN = 'YOUR TOKEN HERE'


def hello(update: Update, context: CallbackContext):
    update.message.reply_text('hello {}'.format(update.message.from_user.name))


updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.start_polling()
updater.idle()
