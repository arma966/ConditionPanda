from requests import get
from threading import Thread
import os 



def send_threaded(message):
    base = "https://api.telegram.org/bot"\
            + os.environ.get('TELEGRAM_TOKEN') \
            +"/sendMessage?chat_id=-543252905&text="
    url = base+message
    get(url)

def send_telegram(message):
    bot_process = Thread(target=send_threaded, args=[message])
    bot_process.name = 'TelegramThread'
    bot_process.start()

