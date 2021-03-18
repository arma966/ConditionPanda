# from tkinter import Label,Entry, Tk, Button
from tkinter import Tk, Label, Entry, Button, W ,SW, Checkbutton, BooleanVar
from tkinter.ttk import Combobox
from json import load, dump
from os.path import join, realpath, dirname
from DeweAutomation import isRunning, deweAuto
from deweUtils import DeweInit, getMeasName
from win32com.client import Dispatch
from datetime import date
import time
import JsonExport as je
import JsonToInflux as jti


def writeConfig():
    global Config
    global DirE
    
    Config["Dewesoft"]["DataDir"]           = DirE.get()
    Config["Dewesoft"]["SetupFile"]         = SetupE.get()
    Config["InfluxDB"]["Measurement"]       = MeasE.get()
    Config["InfluxDB"]["Org"]               = OrgE.get()
    Config["InfluxDB"]["KPI Bucket"]        = Bucket1E.get()
    Config["InfluxDB"]["Client URL"]        = UrlE.get()
    Config["Dewesoft"]["Record duration"]   = RecE.get()
    Config["Dewesoft"]["Sampling frequency"] = ComboSampleR.get()
    
    filePath = join(mypath,ConfigFile)
    with open(filePath,'w') as f:
        dump(Config,f,indent="\t")
    f.close()
    dw.Trigger.PostTime = int(Config["Dewesoft"]["Record duration"])
    dw.Measure()
    dw.MeasureSampleRate = int(Config["Dewesoft"]["Sampling frequency"])
    print("Configuration saved")
        
def Load():
    dw.Measure()
    je.to_couchDB()
    dateToLoad = str(date.today())
    jti.to_influx(dateToLoad)

def Measure():
    msname = getMeasName()
    FileName = Config["Dewesoft"]['FileName']+msname
    deweAuto(dw,FileName, DataDir)
    
    
    if checkVar.get() == True:
        print("Auto loading")
        dw.Measure()
        je.to_couchDB()
        dateToLoad = str(date.today())
        jti.to_influx(dateToLoad)    
    
def LoadSetup():
    dw.LoadSetup(join(mypath,Config["Dewesoft"]["SetupFile"]))

def SetAutoLoad():
    global Config
    
    Config["InfluxDB"]["AutoLoad"] = str(checkVar.get())
    filePath = join(mypath,'Config.json')
    with open(filePath,'w') as f:
        dump(Config,f,indent="\t")
    f.close()
    
root = Tk()

mypath = dirname(realpath(__file__))
root.iconbitmap(join(mypath,'icon.ico'))
root.title("Configuration")

# Read config file
ConfigFile = "Config.json"
try: 
    with open(ConfigFile) as f:
        Config = load(f)
    f.close()
except:
    print("Can't open the configuration file.")

SampleList = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]
windowWidth = int(750)
windowHeight = int(300)
root.minsize(windowWidth,windowHeight)
root.resizable(0, 0)

EntryLen = 70

InfluxLabel = Label(root, text = "Dewesoft config")
InfluxLabel.grid(row=0,column=0,pady = 4, sticky=SW)

DirLabel = Label(root, text = "Data directory")
DirLabel.grid(row=1,column=0, sticky=W)
DirE = Entry(root, width = EntryLen)
DirE.grid(row=1,column=1,padx = 20,pady = 4, sticky=W)

SetupLabel = Label(root, text = "Setup file")
SetupLabel.grid(row=2,column=0, sticky=W)
SetupE = Entry(root, width = EntryLen)
SetupE.grid(row=2,column=1,padx = 20,pady = 4, sticky=W)

RecLabel = Label(root, text = "Record duration [ms]")
RecLabel.grid(row=3,column=0, sticky=W)
RecE = Entry(root, width = EntryLen)
RecE.grid(row=3,column=1,padx = 20,pady = 4, sticky=W)

SamplerLabel = Label(root, text = "Sample rate [Hz]")
SamplerLabel.grid(row=4,column=0, sticky=W)

ComboSampleR = Combobox(root, values = SampleList)
ComboSampleR.grid(row=4,column=1,padx = 20,pady = 4, sticky=W)

InfluxLabel = Label(root, text = " ")
InfluxLabel.grid(row=5,column=0,pady = 4, sticky=SW)

InfluxLabel = Label(root, text = "Influx config")
InfluxLabel.grid(row=6,column=0,pady = 4, sticky=SW)

MeasLabel = Label(root, text = "Measurement")
MeasLabel.grid(row=7,column=0, sticky=W)
MeasE = Entry(root, width = EntryLen)
MeasE.grid(row=7,column=1,padx = 20,pady = 4, sticky=W)

OrgLabel = Label(root, text = "Organization")
OrgLabel.grid(row=8,column=0, sticky=W)
OrgE = Entry(root, width = EntryLen)
OrgE.grid(row=8,column=1,padx = 20,pady = 4, sticky=W)

Bucket1Label = Label(root, text = "Stat bucket name")
Bucket1Label.grid(row=9,column=0, sticky=W)
Bucket1E = Entry(root, width = EntryLen)
Bucket1E.grid(row=9,column=1,padx = 20,pady = 4, sticky=W)

UrlLabel = Label(root, text = "Client URL")
UrlLabel.grid(row=10,column=0, sticky=W)
UrlE = Entry(root, width = EntryLen)
UrlE.grid(row=10,column=1,padx = 20,pady = 4, sticky=W)

checkVar = BooleanVar()
checkAutoload = Checkbutton(root, text='Auto load',variable=checkVar, 
                            onvalue=True, offvalue=False, command=SetAutoLoad)
checkAutoload.place(x = round(0.8*windowWidth), y = round(.9*windowHeight))

ReloadBtn = Button(root, text = "Reload setup",width = 16, command=LoadSetup)
ReloadBtn.place(x = round(0.8*windowWidth), y = round(0.2*windowHeight))

SaveBtn = Button(root, text = "Save",width = 16, command=writeConfig)
SaveBtn.place(x = round(0.8*windowWidth), y = round(0.4*windowHeight))

MeasureBtn = Button(root, text = "Measure",width = 16, command=Measure)
MeasureBtn.place(x = round(0.8*windowWidth), y = round(0.6*windowHeight))

LoadBtn = Button(root, text = "Load",width = 16, command=Load)
LoadBtn.place(x = round(0.8*windowWidth), y = round(0.8*windowHeight))


DirE.insert(0, Config["Dewesoft"]["DataDir"])
SetupE.insert(0, Config["Dewesoft"]["SetupFile"])
MeasE.insert(0, Config["InfluxDB"]["Measurement"])
OrgE.insert(0, Config["InfluxDB"]["Org"])
Bucket1E.insert(0, Config["InfluxDB"]["KPI Bucket"])
UrlE.insert(0, Config["InfluxDB"]["Client URL"])
RecE.insert(0, Config["Dewesoft"]["Record duration"])
ComboSampleR.insert(0, Config["Dewesoft"]["Sampling frequency"])
checkVar.set(Config["InfluxDB"]["AutoLoad"])

DataDir = Config["Dewesoft"]["DataDir"]
SetupFile = Config["Dewesoft"]["SetupFile"]
PostTime    = Config["Dewesoft"]["Record duration"]

# Check if the application is already running
isReady = isRunning()
dw = Dispatch("Dewesoft.App")

if not(isReady):
    DeweInit(dw, DataDir, SetupFile)
    dw.Trigger.PostTime = PostTime
    print('Waiting for the sensor to set-up (15s)')
    time.sleep(15)
print("Ready")

root.mainloop()
