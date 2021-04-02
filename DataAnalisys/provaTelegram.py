def hello_world(update, context):
    bot.send_message(chat_id=update.effective_chat.id, text='Hello, World') 
    
from telegram import *
from telegram.ext import *

bot = Bot("1619431138:AAEhmsVGYbm4HbQTCsoZbQyuejtCTiSiDMY")

updater = Updater("1619431138:AAEhmsVGYbm4HbQTCsoZbQyuejtCTiSiDMY",use_context=True)

dispatcher = updater.dispatcher

start_value = CommandHandler('hello', hello_world)

dispatcher.add_handler(start_value)

updater.start_polling()