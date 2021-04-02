from requests import get
from threading import Thread

def send_threaded(message):
    base = "https://api.telegram.org/bot1619431138:AAEhmsVGYbm4HbQTCsoZbQyuejtCTiSiDMY/"
    base1 = "sendMessage?chat_id=-543252905&text="
    url = base+base1+message
    get(url)

def send_telegram(message):
    telegram_thread = Thread(target=send_threaded, args=[message])
    telegram_thread.name = 'TelegramThread'
    telegram_thread.start()

if __name__ == '__main__':
    message = "Pippo1"
    send_telegram(message)

        
