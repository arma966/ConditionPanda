
#----------------------------------------------------------------------------------------------------------------
# Dewesoft automation example for Python
#----------------------------------------------------------------------------------------------------------------
# Author: Dewesoft
# Notes:
#   - tested with Python 3.4
#----------------------------------------------------------------------------------------------------------------

from win32com.client import Dispatch
import time
import psutil
import json 
from deweUtils import DeweInit, getMeasName

msname = getMeasName()

# Read configuration file 
with open('Config.json','r') as myfile:
    configData = myfile.read()
myfile.close()

config = json.loads(configData)

DataDir = config['DataDir']
SetupFile = config['SetupFile']
FileName = config['FileName']+msname

# Check if the application is already running
ready = False
for proc in psutil.process_iter(['name']):
    if proc.info['name'] == 'DEWEsoft.exe':
        print('Dewesoft app already running')
        ready = True

dw = Dispatch("Dewesoft.App")
WaitOnStart = False  
if not(ready):
    DeweInit(dw, DataDir, SetupFile)
    WaitOnStart = True

# Routine ____________________________________________________________________

dw.Measure()
print('Starting Measurement')
if WaitOnStart:
    print('Waiting for sensor setup (15s)')
    time.sleep(15)
print('Starting Storing')


dw.StartStoring(FileName + '.dxd')
dw.ManualStart()
time.sleep(1)
finished = False
while not(finished):
    time.sleep(1)
    
    # Check if the last event is "Storing stopped"
    nEvents = dw.EventList.Count - 1
    if dw.EventList.Item(nEvents).Type_ == 2:
        print("Done")
        finished = True

dw.Stop()

dw.Analyze()
dw.OfflineCalc.Calculate()
try:
    dw.ExportData(7,2,DataDir + "\\" + FileName)
except:
    print("Exporting failed")
    
