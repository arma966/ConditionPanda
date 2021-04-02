import time
import psutil
from os.path import join
from datetime import datetime
import telegramUtils as tu

def isRunning():
    isReady = False
    for proc in psutil.process_iter(["name"]):
        if proc.info["name"] == "DEWEsoft.exe":
            print("Dewesoft app already running")
            isReady = True
    return isReady


def deweAuto(dw, FileName, DataDir):
    # Routine ________________________________________________________________
    print("\n-------Dewesoft-------")
    dw.Measure()
    print("Start storing")
    tu.send_telegram("Start storing")
    dw.StartStoring(FileName + ".dxd")
    dw.ManualStart()

    time.sleep(1)

    finished = False
    while not (finished):
        time.sleep(1)
        # Check if the last event is "Storing stopped" (type 2)
        
        for _ in range(20):
            try:
                nEvents = dw.EventList.Count - 1
                last_event = dw.EventList.Item(nEvents).Type_
            except Exception as e:
                print("Exception com error")
                time.sleep(1)
        if last_event == 2:
            print("Done")
            finished = True
            
            
    for _ in range(10):
        if dw.StoreEngine.Storing is True:
            print("-------------Storing True -------------------")
            dw.Stop()
            time.sleep(0.5)
    
    print("Measure completed")

    # Calculate offline math (FFT, statistics, etc...)
    dw.Analyze()
    dw.OfflineCalc.Calculate()
    
    print("Exporting data")
    try:
        dw.ExportData(7, 2, join(DataDir, FileName))
    except Exception as e:
        message = "Exporting failed\n Exception: {}"
        print(message.format(e))
    else:
        print("Data exported successfully")
        tu.send_telegram("Data exported successfully")
    dw.Measure()


def DeweInit(dw, data_dir, setup_file):
    print("Initializing Dewesoft... ")

    dw.Init()
    dw.Enabled = 1
    dw.Visible = 1
    print("Done.")

    # set window dimensions
    dw.Top = 0
    dw.Left = 0
    dw.Width = 1024
    dw.Height = 768

    # build channel list
    dw.Data.BuildChannelList()

    with open(setup_file, "r") as file:
        data = file.read()
    file.close

    dw.LoadSetupFromXML(data)

    try:
        dw.SetMainDataDir(data_dir)
    except AttributeError:
        print("The configuration Dewesoft directory doesn't exist.")
        print("Make sure to use the production configuration file")
        return


def getMeasName():
    MeasName = str(datetime.now())
    MeasName = MeasName[: MeasName.find(".")]
    MeasName = MeasName.replace(":", "")
    MeasName = MeasName.replace("-", "")
    MeasName = MeasName.replace(" ", "")
    return MeasName
