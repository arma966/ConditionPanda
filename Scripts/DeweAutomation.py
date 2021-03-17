import time
import psutil
from os.path import join

def isRunning():
    isReady = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'DEWEsoft.exe':
            print('Dewesoft app already running')
            isReady = True
    return isReady
    
def deweAuto(dw, FileName, DataDir):
    # Routine ____________________________________________________________________  
    dw.Measure()   
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
    
    # Calculate offline math (FFT, statistics, etc...)
    dw.Analyze()
    dw.OfflineCalc.Calculate()
    
    try:
        print("Exporting data")
        dw.ExportData(7,2,join(DataDir,FileName))
    except:
        print("Exporting failed")
    dw.Measure()
    print("Measure completed")
    
    
    
