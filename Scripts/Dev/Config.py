# from tkinter import Label,Entry, Tk, Button
from tkinter import Tk, Label, Entry, Button
from json import load, dump
from os.path import join, realpath, dirname
from subprocess import run
from DeweAutomation import *
from deweUtils import DeweInit, getMeasName
from win32com.client import Dispatch
import time
from json import loads
from SendToInflux import *


def writeConfig():
    global Config
    global DirE
    
    Config["DataDir"] = DirE.get()
    Config["SetupFile"] = SetupE.get()
    Config["Measurement"] = MeasE.get()
    Config["org"] = OrgE.get()
    Config["bucket"] = Bucket1E.get()
    Config["RawBucket"] = Bucket2E.get()
    Config["clientURL"] = UrlE.get()
    Config["RecordDuration"] = RecE.get()
    Config["SampleRate"] = SamplerE.get()
    
    filePath = join(mypath,'Config.json')
    with open(filePath,'w') as f:
        dump(Config,f,indent="\t")
    f.close()
    dw.Trigger.PostTime = int(Config["RecordDuration"])
    dw.Measure()
    dw.MeasureSampleRate = int(Config["SampleRate"])
        
def Load():
    dw.Measure()
    uploadData()

def Measure():
    msname = getMeasName()
    FileName = config['FileName']+msname
    deweAuto(dw,FileName, DataDir)
    
    
root = Tk()

mypath = dirname(realpath(__file__))
root.iconbitmap(join(mypath,'icon.ico'))
root.title("Configuration")

# Read config file
try: 
    ConfigFile = open(join(mypath,'Config.json'))
    Config = load(ConfigFile)
    ConfigFile.close()
except:
    print("Can't open the configuration file.")

windowWidth = int(750)
windowHeight = int(260)
root.minsize(windowWidth,windowHeight)
root.resizable(0, 0)

EntryLen = 70
DirLabel = Label(root, text = "Data directory")
DirLabel.grid(row=0,column=0)
DirE = Entry(root, width = EntryLen)
DirE.grid(row=0,column=1,padx = 40,pady = 4)

SetupLabel = Label(root, text = "Setup file")
SetupLabel.grid(row=1,column=0)
SetupE = Entry(root, width = EntryLen)
SetupE.grid(row=1,column=1,padx = 20,pady = 4)

MeasLabel = Label(root, text = "Measurement")
MeasLabel.grid(row=2,column=0)
MeasE = Entry(root, width = EntryLen)
MeasE.grid(row=2,column=1,padx = 20,pady = 4)

OrgLabel = Label(root, text = "Organization")
OrgLabel.grid(row=3,column=0)
OrgE = Entry(root, width = EntryLen)
OrgE.grid(row=3,column=1,padx = 20,pady = 4)

Bucket1Label = Label(root, text = "Stat bucket name")
Bucket1Label.grid(row=4,column=0)
Bucket1E = Entry(root, width = EntryLen)
Bucket1E.grid(row=4,column=1,padx = 20,pady = 4)

Bucket2Label = Label(root, text = "Raw bucket name")
Bucket2Label.grid(row=5,column=0)
Bucket2E = Entry(root, width = EntryLen)
Bucket2E.grid(row=5,column=1,padx = 20,pady = 4)

UrlLabel = Label(root, text = "Client URL")
UrlLabel.grid(row=6,column=0)
UrlE = Entry(root, width = EntryLen)
UrlE.grid(row=6,column=1,padx = 20,pady = 4)

RecLabel = Label(root, text = "Record duration [ms]")
RecLabel.grid(row=7,column=0)
RecE = Entry(root, width = EntryLen)
RecE.grid(row=7,column=1,padx = 20,pady = 4)

SamplerLabel = Label(root, text = "Sample rate [Hz]")
SamplerLabel.grid(row=8,column=0)
SamplerE = Entry(root, width = EntryLen)
SamplerE.grid(row=8,column=1,padx = 20,pady = 4)

SaveBtn = Button(root, text = "Save",width = 16, command=writeConfig)
SaveBtn.place(x = round(0.8*windowWidth), y = round(0.2*windowHeight))

MeasureBtn = Button(root, text = "Measure",width = 16, command=Measure)
MeasureBtn.place(x = round(0.8*windowWidth), y = round(0.4*windowHeight))

LoadBtn = Button(root, text = "Load",width = 16, command=Load)
LoadBtn.place(x = round(0.8*windowWidth), y = round(0.6*windowHeight))


DirE.insert(0, Config["DataDir"])
SetupE.insert(0, Config["SetupFile"])
MeasE.insert(0, Config["Measurement"])
OrgE.insert(0, Config["org"])
Bucket1E.insert(0, Config["bucket"])
Bucket2E.insert(0, Config["RawBucket"])
UrlE.insert(0, Config["clientURL"])
RecE.insert(0, Config["RecordDuration"])
SamplerE.insert(0, Config["SampleRate"])

msname = getMeasName()

# Read configuration file 
with open('Config.json','r') as myfile:
    configData = myfile.read()
myfile.close()
config = loads(configData)

DataDir = config['DataDir']
SetupFile = config['SetupFile']
# FileName = config['FileName']+msname
PostTime    = int(config['RecordDuration'])

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
