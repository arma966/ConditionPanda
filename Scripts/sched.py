import telegramUtils as tu
from os.path import join, realpath, dirname,normpath
import DeweAutomation as dwa
from win32com.client import Dispatch
import JsonExport as je

import CouchInflux as ci
import schedule
import threading
import configparser
import sys
import time

def Load():
    dw.Measure()
    je.to_couchDB()
    ci.to_influx()


def Measure(dw, DataDir):
    msname = dwa.getMeasName()
    FileName = config["DEWESOFT"]["file_name"] + msname
    dwa.deweAuto(dw, FileName, DataDir)

    Load()

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
    time.sleep(15)
else:
    dw = Dispatch("Dewesoft.App")
print("Ready")

schedule.clear()
schedule.every(1).minutes.do(Measure,
                             dw=dw, 
                             DataDir=DataDir)
while True:
    schedule.run_pending()
    time.sleep(5)