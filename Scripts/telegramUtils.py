from requests import get
from threading import Thread
from telegram.ext import * 

def send_threaded(message):
    base = "https://api.telegram.org/bot1619431138:AAEhmsVGYbm4HbQTCsoZbQyuejtCTiSiDMY/"
    base1 = "sendMessage?chat_id=-543252905&text="
    url = base+base1+message
    get(url)

def send_telegram(message):
    telegram_thread = Thread(target=send_threaded, args=[message])
    telegram_thread.name = 'TelegramThread'
    telegram_thread.start()


def sample_responses(input_message):
    user_message = str(input_message).lower()
    
    if user_message in ["stato"]:
        return "Funzionante"
    elif user_message in ["state"]:
        return "Running"
    elif user_message in ["we","hei bello","come va","tutto ok?"]:
        return "Tutto apposto fratè!"
    else: return "?"

def handle_message(update,context):
    text = str(update.message.text).lower()
    response = sample_responses(text)
    update.message.reply_text(response)

def run_bot():
    KEY_API = "1619431138:AAEhmsVGYbm4HbQTCsoZbQyuejtCTiSiDMY"
    updater = Updater(KEY_API, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(MessageHandler(Filters.text,handle_message))
    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    message = "Starting the bot"
    send_telegram(message)
    run_bot()
        