# from tkinter import Label,Entry, Tk, Button
from tkinter import Tk, Label, Entry, Button, W, SW, Checkbutton, BooleanVar
from tkinter.ttk import Combobox
from os.path import join, realpath, dirname
import DeweAutomation as dwa
from win32com.client import Dispatch
import time
import JsonExport as je
import configparser
from os.path import normpath
import sys
import CouchInflux as ci
import telegramUtils as tu

def test_configFile():
    production_key_list = [
        "org",
        "token",
        "measurement",
        "influxurl",
        "kpibucket",
        "auto_load",
        "log_dir",
        "data_dir",
        "setup_file",
        "file_name",
        "record_duration",
        "sampling_frequency",
        "sensor_name",
        "couch_dir",
        "couch_url",
        "username",
        "password",
        "database",
    ]
    key_list = []
    for section in config:
        for key in config[section]:
            key_list.append(key)

    # Check if key_list is a subset of production_key_list
    common_elements = [ele for ele in key_list if (ele in production_key_list)]

    missing_keys = []
    for key in production_key_list:
        if key not in common_elements:
            missing_keys.append(key)
    return missing_keys


def writeConfig():
    config["DEWESOFT"]["data_dir"] = DirE.get()
    config["DEWESOFT"]["setup_file"] = SetupE.get()
    config["DEWESOFT"]["record_duration"] = RecE.get()
    config["DEWESOFT"]["sampling_frequency"] = ComboSampleR.get()
    config["INFLUXDB"]["measurement"] = MeasE.get()
    config["INFLUXDB"]["Org"] = OrgE.get()
    config["INFLUXDB"]["KPIbucket"] = Bucket1E.get()
    config["INFLUXDB"]["InfluxURL"] = UrlE.get()
    config["COUCHDB"]["couch_url"] = c_UrlE.get()
    config["COUCHDB"]["username"] = c_userE.get()
    config["COUCHDB"]["password"] = c_passE.get()
    config["COUCHDB"]["database"] = c_dbE.get()

    with open(ConfigFile, "w") as f:
        config.write(f)
    f.close()
    dw.Trigger.PostTime = int(config["DEWESOFT"]["record_duration"])
    dw.Measure()
    dw.MeasureSampleRate = int(config["DEWESOFT"]["sampling_frequency"])
    print("Configuration saved")


def Load():
    dw.Measure()
    je.to_couchDB()
    ci.to_influx()


def Measure():
    msname = dwa.getMeasName()
    FileName = config["DEWESOFT"]["file_name"] + msname
    dwa.deweAuto(dw, FileName, DataDir)

    if checkVar.get() is True:
        print("Auto loading")
        dw.Measure()
        je.to_couchDB()
        ci.to_influx()


def LoadSetup():
    dw.LoadSetup(join(mypath, config["DEWESOFT"]["setup_file"]))


def SetAutoLoad():
    config["INFLUXDB"]["auto_load"] = str(checkVar.get())
    with open(ConfigFile, "w") as f:
        config.write(f)
    f.close()


# Read config file
global config
global ConfigFile
ConfigFile = "config.ini"
config = configparser.ConfigParser()
response = config.read(ConfigFile)
if response == []:
    print("Can't find the config file")
    sys.exit()
else:
    missing_keys = test_configFile()
    if missing_keys:
        print("Invalid configuration file, the following keys are missing:")
        print(missing_keys)
        sys.exit()


root = Tk()

mypath = dirname(realpath(__file__))
root.iconbitmap(join(mypath, "icon.ico"))
root.title("Configuration")


# Graphics
# ______________________________________________________________________________
SampleList = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]
windowWidth = int(750)
windowHeight = int(300)
root.minsize(windowWidth, windowHeight)
root.resizable(0, 0)

EntryLen = 70

GenerigLabel = Label(root, text="Dewesoft")
GenerigLabel.grid(row=0, column=0, pady=4, sticky=SW)

DirLabel = Label(root, text="Data directory")
DirLabel.grid(row=1, column=0, sticky=W)
DirE = Entry(root, width=EntryLen)
DirE.grid(row=1, column=1, padx=20, pady=4, sticky=W)

SetupLabel = Label(root, text="Setup file")
SetupLabel.grid(row=2, column=0, sticky=W)
SetupE = Entry(root, width=EntryLen)
SetupE.grid(row=2, column=1, padx=20, pady=4, sticky=W)

RecLabel = Label(root, text="Record duration [ms]")
RecLabel.grid(row=3, column=0, sticky=W)
RecE = Entry(root, width=EntryLen)
RecE.grid(row=3, column=1, padx=20, pady=4, sticky=W)

SamplerLabel = Label(root, text="Sample rate [Hz]")
SamplerLabel.grid(row=4, column=0, sticky=W)

ComboSampleR = Combobox(root, values=SampleList)
ComboSampleR.grid(row=4, column=1, padx=20, pady=4, sticky=W)

GenerigLabel = Label(root, text=" ")
GenerigLabel.grid(row=5, column=0, pady=4, sticky=SW)

GenerigLabel = Label(root, text="Influx")
GenerigLabel.grid(row=6, column=0, pady=4, sticky=SW)

MeasLabel = Label(root, text="Measurement")
MeasLabel.grid(row=7, column=0, sticky=W)
MeasE = Entry(root, width=EntryLen)
MeasE.grid(row=7, column=1, padx=20, pady=4, sticky=W)

OrgLabel = Label(root, text="Organization")
OrgLabel.grid(row=8, column=0, sticky=W)
OrgE = Entry(root, width=EntryLen)
OrgE.grid(row=8, column=1, padx=20, pady=4, sticky=W)

Bucket1Label = Label(root, text="Stat bucket name")
Bucket1Label.grid(row=9, column=0, sticky=W)
Bucket1E = Entry(root, width=EntryLen)
Bucket1E.grid(row=9, column=1, padx=20, pady=4, sticky=W)

UrlLabel = Label(root, text="Client URL")
UrlLabel.grid(row=10, column=0, sticky=W)
UrlE = Entry(root, width=EntryLen)
UrlE.grid(row=10, column=1, padx=20, pady=4, sticky=W)

GenerigLabel = Label(root, text=" ")
GenerigLabel.grid(row=11, column=0, pady=4, sticky=SW)

GenerigLabel = Label(root, text="Couch")
GenerigLabel.grid(row=12, column=0, pady=4, sticky=SW)

Curl = Label(root, text="CouchDB URL")
Curl.grid(row=13, column=0, sticky=W)
c_UrlE = Entry(root, width=EntryLen)
c_UrlE.grid(row=13, column=1, padx=20, pady=4, sticky=W)

Cdb = Label(root, text="Database")
Cdb.grid(row=14, column=0, sticky=W)
c_dbE = Entry(root, width=EntryLen)
c_dbE.grid(row=14, column=1, padx=20, pady=4, sticky=W)

c_user = Label(root, text="Username")
c_user.grid(row=15, column=0, sticky=W)
c_userE = Entry(root, width=EntryLen)
c_userE.grid(row=15, column=1, padx=20, pady=4, sticky=W)

c_pass = Label(root, text="Password")
c_pass.grid(row=16, column=0, sticky=W)
c_passE = Entry(root, width=EntryLen, show="\u2022")
c_passE.grid(row=16, column=1, padx=20, pady=4, sticky=W)


checkVar = BooleanVar()
checkAutoload = Checkbutton(
    root,
    text="Auto load",
    variable=checkVar,
    onvalue=True,
    offvalue=False,
    command=SetAutoLoad,
)
checkAutoload.place(x=round(0.8 * windowWidth), y=round(0.9 * windowHeight))

ReloadBtn = Button(root, text="Reload setup", width=16, command=LoadSetup)
ReloadBtn.place(x=round(0.8 * windowWidth), y=round(0.2 * windowHeight))

SaveBtn = Button(root, text="Save", width=16, command=writeConfig)
SaveBtn.place(x=round(0.8 * windowWidth), y=round(0.4 * windowHeight))

MeasureBtn = Button(root, text="Measure", width=16, command=Measure)
MeasureBtn.place(x=round(0.8 * windowWidth), y=round(0.6 * windowHeight))

LoadBtn = Button(root, text="Load", width=16, command=Load)
LoadBtn.place(x=round(0.8 * windowWidth), y=round(0.8 * windowHeight))
# _____________________________________________________________________________

DirE.insert(0, config["DEWESOFT"]["data_dir"])
SetupE.insert(0, config["DEWESOFT"]["setup_file"])
RecE.insert(0, config["DEWESOFT"]["record_duration"])
ComboSampleR.insert(0, config["DEWESOFT"]["sampling_frequency"])

MeasE.insert(0, config["INFLUXDB"]["measurement"])
OrgE.insert(0, config["INFLUXDB"]["Org"])
Bucket1E.insert(0, config["INFLUXDB"]["KPIbucket"])
UrlE.insert(0, config["INFLUXDB"]["InfluxURL"])
checkVar.set(bool(config["INFLUXDB"]["auto_load"]))

c_UrlE.insert(0, config["COUCHDB"]["couch_url"])
c_userE.insert(0, config["COUCHDB"]["username"])
c_passE.insert(0, config["COUCHDB"]["password"])
c_dbE.insert(0, config["COUCHDB"]["database"])

DataDir = normpath(config["DEWESOFT"]["data_dir"])
SetupFile = config["DEWESOFT"]["setup_file"]
PostTime = config["DEWESOFT"]["record_duration"]
# Check if the application is already running
if not (dwa.isRunning()):
    dw = Dispatch("Dewesoft.App")
    dwa.DeweInit(dw, DataDir, SetupFile)
    dw.Trigger.PostTime = PostTime
    dw.MeasureSampleRate = int(config["DEWESOFT"]["sampling_frequency"])
    print("Waiting for the sensor to set-up (15s)")
    time.sleep(15)
else:
    dw = Dispatch("Dewesoft.App")
print("Ready")

root.mainloop()
