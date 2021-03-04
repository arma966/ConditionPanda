# from tkinter import Label,Entry, Tk, Button
from tkinter import Tk, Label, Entry, Button
from json import load, dump
from os.path import join, realpath, dirname


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
    
    filePath = join(mypath,'Config.json')
    with open(filePath,'w') as f:
        dump(Config,f,indent="\t")
    
    
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

windowWidth = int(640)
windowHeight = int(250)
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

SaveBtn = Button(root, text = "Save",width = 16, command=writeConfig)
SaveBtn.place(x = round(0.4*windowWidth), y = round(0.84*windowHeight))

DirE.insert(0, Config["DataDir"])
SetupE.insert(0, Config["SetupFile"])
MeasE.insert(0, Config["Measurement"])
OrgE.insert(0, Config["org"])
Bucket1E.insert(0, Config["bucket"])
Bucket2E.insert(0, Config["RawBucket"])
UrlE.insert(0, Config["clientURL"])

root.mainloop()
