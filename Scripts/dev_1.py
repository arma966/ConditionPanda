import DeweAutomation as dwa
from win32com.client import Dispatch
import time
from os.path import join 

DataDir = "C:\\Users\\LattePanda\\Documents\\ConditionPanda\\Scripts\\AutomationData"
SetupFile = "AccSetup2.xml"

if not(dwa.isRunning()):
    dw = Dispatch("Dewesoft.App")
    dwa.DeweInit(dw, DataDir, SetupFile)
    dw.Trigger.PostTime = 2000
    dw.MeasureSampleRate = 20000
    print('Waiting for the sensor to set-up (15s)')
    time.sleep(5)
else:
    dw = Dispatch("Dewesoft.App")
print("Ready")


dw.Measure()
print('Starting Storing')
dw.StartStoring("test_freq" + '.dxd')
dw.ManualStart()

finished = False
while not(finished):
    time.sleep(1)
    # Check if the last event is "Storing stopped"
    nEvents = dw.EventList.Count - 1
    if dw.EventList.Item(nEvents).Type_ == 2:
        print("Done")
        finished = True

dw.Stop()

# Calculate offline math (FFT, statistics, etc...)
dw.Analyze()
dw.OfflineCalc.Calculate()

channel_list = []
flag = True
for i in range(100):
    try:
        channel_list.append(dw.Data.UsedChannels(i).Name)
    except:
        break

index = []
name = []    
for i,s in enumerate(channel_list):
    if not("FFT" in s):
        dw.Data.UsedChannels(i).Exported = False
        
        
dw.ExportData(7,2,join(DataDir,"provaCSV2"))