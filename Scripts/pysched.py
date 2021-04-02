import telegramUtils as tu
from os.path import join, realpath, dirname,normpath
import DeweAutomation as dwa
from win32com.client import Dispatch
import JsonExport as je

import CouchInflux as ci
import schedule
import configparser
import time
import os


def Load(dw):
    dw.Measure()
    je.to_couchDB()
    ci.to_influx()


def Measure(dw, DataDir,schedule_list):
    msname = dwa.getMeasName()
    FileName = config["DEWESOFT"]["file_name"] + msname
    dwa.deweAuto(dw, FileName, DataDir)

    Load(dw)
    
    del schedule_list[0]
    with open("schedule.txt","w") as f:
        for item in schedule_list:
            f.writelines(item)
    f.close()
    
def read_schedule():
    from datetime import datetime
    with open("schedule.txt") as f:
        content = f.readlines()
    f.close()
    schedule_list = list(content)
    for i,time_scheduled in enumerate(schedule_list):
        try:
            datetime.strptime(time_scheduled.split("\n")[0],
                              "%H:%M:%S")
        except ValueError:
            print("Scheduled time not valid: {}".format(schedule_list[i]))
            schedule_list.remove(time_scheduled)
    return schedule_list

def build_schedule(schedule_list,dw,DataDir):
    schedule.clear()
    for schedule_time in schedule_list:
        schedule.every().day.at(schedule_time).do(Measure,
                                                  dw=dw, 
                                                  DataDir=DataDir,
                                                  schedule_list=schedule_list)

def update_schedule(schedule_list,dw,DataDir):
    def difference(list1, list2):
        if len(list1) > len(list2):
            long_list = list1
            short_list = list2
        elif len(list1) < len(list2):
            long_list = list2
            short_list = list1
        else: return []
        
        temp = set(short_list)
        difference_list = [value for value in long_list if value not in temp]
        return difference_list
    
    
    new_schedule = read_schedule()
    new_entries = difference(schedule_list,new_schedule)
    if not new_entries: 
        return schedule_list
    else:
        build_schedule(new_schedule,dw,DataDir)
        print("Measure added at {}".format(new_entries))
        return new_schedule
    
def save_pid():
    print("Process ID: {}".format(os.getpid()))
    byte_pid = os.getpid().to_bytes(3,'big')
    with open("schedulerPID","wb") as f:
        f.write(byte_pid)
    f.close 
    
    
def start_schedule():
    tu.send_telegram("Scheduler is running")
    save_pid()
    # Read config file
    global config
    global ConfigFile
    
    ConfigFile = "config.ini"
    config = configparser.ConfigParser()
    response = config.read(ConfigFile)
    
    
    DataDir = normpath(config["DEWESOFT"]["data_dir"])
    SetupFile = config["DEWESOFT"]["setup_file"]
    PostTime = config["DEWESOFT"]["record_duration"]
    # Check if the application is already running
    if not (dwa.isRunning()):
        dw = Dispatch("Dewesoft.App")
        dwa.DeweInit(dw, DataDir, SetupFile)
        dw.Trigger.PostTime = PostTime
        dw.MeasureSampleRate = int(config["DEWESOFT"]["sampling_frequency"])
        print("Waiting for the sensor to set-up (15s)")#
        tu.send_telegram("Waiting for the sensor to set-up (15s)")
        time.sleep(15)
    else:
        dw = Dispatch("Dewesoft.App")
    tu.send_telegram("Scheduler is ready")
    print("Ready")
    
    scheduled_time = read_schedule()
    build_schedule(scheduled_time,dw,DataDir)
    
    
    while True:
        scheduled_time = update_schedule(scheduled_time,dw,DataDir)
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    start_schedule()