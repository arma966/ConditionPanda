import time
import psutil
from os.path import join
from datetime import datetime


def isRunning():
    isReady = False
    for proc in psutil.process_iter(["name"]):
        if proc.info["name"] == "DEWEsoft.exe":
            print("Dewesoft app already running")
            isReady = True
    return isReady


def deweAuto(dw, FileName, DataDir):
    # Routine ________________________________________________________________
    dw.Measure()
    print("Starting Storing")
    dw.StartStoring(FileName + ".dxd")
    dw.ManualStart()

    time.sleep(1)

    finished = False
    while not (finished):
        time.sleep(1)
        # Check if the last event is "Storing stopped"
        nEvents = dw.EventList.Count - 1
        if dw.EventList.Item(nEvents).Type_ == 2:
            print("Done")
            finished = True

    dw.Stop()
    print("Measure completed")

    # Calculate offline math (FFT, statistics, etc...)
    dw.Analyze()
    dw.OfflineCalc.Calculate()
    
    print("Exporting data")
    try:
        dw.ExportData(7, 2, join(DataDir, FileName))
    except Exception as e:
        print("Exporting failed")
        print("Exception: " + str(e))
    else:
        print("Data exported successfully")
    dw.Measure()


def DeweInit(dw, data_dir, setup_file):
    print("Initializing Dewesoft... ")

    dw.Init()
    dw.Enabled = 1
    dw.Visible = 1
    print("done.")

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
        dw.SetMaindata_dir(data_dir)
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
