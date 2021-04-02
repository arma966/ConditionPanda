from requests import get
from threading import Thread
from telegram.ext import *
import os 
from random import randint
from datetime import datetime
import requests
import time


def terminator(update,context):
    import psutil 
    with open("schedulerPID","rb") as f:
        byte_pid = f.read()
        sched_pid = int.from_bytes(byte_pid, 'big')
    f.close
    
    for proc in psutil.process_iter():
        if proc.name()=="python.exe" and proc.pid == sched_pid:
            os.system("CALL taskkill /PID {} /F".format(proc.pid))
            context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Schedule process terminated")
        elif proc.name() == "DEWEsoft.exe":
            os.system("CALL taskkill /PID {} /F".format(proc.pid))
            context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Dewesoft process terminated")
            
def restart(update,context):
    terminator(update,context)
    os.system("start /B start cmd.exe @cmd /k RunSched.bat")
    

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


def get_schedule(update,context):
    with open("schedule.txt","r") as f:
        schedule_content = f.read()
    f.close()
    response = schedule_content.replace(" ", "\n")
    if response == "": response = "There are not scheduled measures"
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=response)
    
def schedule_measure(update,context):
    def zero_pad(time_string):
        manipulator = time_string.split(":")
        for i,ele in enumerate(manipulator):
            if len(ele) == 1:
                manipulator[i] = '0'+ele
        padded_time_string = ":".join(manipulator)
        return padded_time_string
    
    time_string = str(update.message.text).split(" ")[1]
    padded_time = zero_pad(time_string)
    try:
        datetime.strptime(padded_time, "%H:%M:%S")
    except (ValueError, IndexError):
        update.message.reply_text("Invalid format")
    else:
        with open("schedule.txt","a") as f:
            f.write(padded_time + "\n")
        f.close()
        update.message.reply_text("Measure scheduled at {}".format(padded_time))
    
    
def help_command(update, context):
    help_list = ["/schedule HH:MM:SS to schedule a measure\n",
                "/last to get the last uploaded measure\n",
                "/getschedule to get the scheduled measures\n",
                "/getconfig to get che config file\n",
                "/gethistory to get che table history\n"]
    resp = "".join(help_list)            
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=response)
    

def handle_message(update,context):
    text = str(update.message.text).lower()
    response = sample_responses(text)
    update.message.reply_text(response)


def get_file(file_name):
    for i in range(3):
        try:
            file = open(file_name,"rb")
        except Exception as e: 
            if i == 2:
                print("An exception occurred: {}".format(e))
                context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="someting went wrong")
                return None
            time.sleep(0.2)
    
        else:
            return file
    
def get_config(update,context):
    CHAT_ID = "-543252905"
    base = "https://api.telegram.org/bot{}/sendDocument?chat_id={}"
    
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Sending config file")
    config_file = get_file("config.ini")
    response = requests.post(base.format(os.environ.get('TELEGRAM_TOKEN'),
                                         CHAT_ID), 
                             files={'document': config_file})
    config_file.close()

def get_history(update,context):
    CHAT_ID = "-543252905"
    base = "https://api.telegram.org/bot{}/sendDocument?chat_id={}"
    
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Sending config file")
    history_file = get_file("history_table.csv")
    response = requests.post(base.format(os.environ.get('TELEGRAM_TOKEN'),
                                         CHAT_ID), 
                             files={'document': history_file})
    history_file.close()
    
    
def clear_schedule(update,context):
    try:
        with open("schedule.txt","w") as f:
            f.write("")
        f.close()
    except FileNotFoundError:
        print("File not found")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Schedule cleared")
        
    
def run_bot():
    updater = Updater(os.environ.get('TELEGRAM_TOKEN'), 
                      use_context=True)
    dp = updater.dispatcher
    
    #dp.add_handler(MessageHandler(Filters.text,handle_message))
    
    dp.add_handler(CommandHandler("schedule",schedule_measure))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('getschedule', get_schedule))
    dp.add_handler(CommandHandler('getconfig', get_config))
    dp.add_handler(CommandHandler('getlast', get_last))
    dp.add_handler(CommandHandler('clearschedule', clear_schedule))
    dp.add_handler(CommandHandler('restart', restart))
    
    updater.start_polling()
    updater.idle()

def get_last(update,context):
    def print_file_info(index):
        with open("history_table.csv","r") as f:
            history_content = f.readlines()
        f.close()
        numeric = history_content[index].split(",")[0].split("-")[1]
        date = (numeric[0:4],numeric[4:6],numeric[6:8])
        hour = (numeric[8:10],numeric[10:12],numeric[12:14])
        in_couch = history_content[-1].split(",")[1]
        in_influx = history_content[index].split(",")[2].split("\n")[0]
        measurement_type = history_content[index].split("-")[0]
        date_string = "-".join(date) + " " + ":".join(hour)
        response="Date: {}\nType: {}\nCouchDB: {}\nInfluxDB: {}".format(date_string,
                                                                        measurement_type,
                                                                        in_couch,
                                                                        in_influx)
        
        context.bot.send_message(chat_id=update.effective_chat.id, text=response)
                
    print_file_info(-2)
    print_file_info(-1)
    


if __name__ == '__main__':
    message = "Starting the bot"
    send_telegram(message)
    run_bot()
    terminator(update,context)
    os.system("start /B start cmd.exe @cmd /k RunSched.bat")
    
        