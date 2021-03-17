# ____________________________________________________________________________
# Utilities to create a dictionary based data structure from the Dewesoft-exported
# files. The data structure is then coverted to the json format. 
#
# Author: Armenante Davide
# Last update: 15/3/2021
# ____________________________________________________________________________

from numpy import loadtxt
from json import dump, load
from os import listdir
from os.path import join, isfile, isdir
from datetime import datetime, timedelta

from pandas import read_csv

def getMetadata(FilePath):
    # Read the firsts few lines of the *FileName* and retrieve the metadata 
    # creating a dictionary.
    metaDictionary =  {}
    read = True
    with open(FilePath) as f:
        while read:
            tmp = f.readline()
            if not(tmp == "\n"):
                if not(tmp.find(":") == -1):
                    s = tmp.strip().split(": ",maxsplit = 1)
                    metaDictionary[s[0]] = s[1]
            else:
                read = False
    f.close()
    return metaDictionary

def getData(FilePath):
    # Skip the rows which contain the metadata and get the data from *FileName*
    # as a numpy array. 
    
    # Get the number of rows to skip
    read = True
    with open(FilePath) as f:
        i = 0
        while read:
            tmp = f.readline()
            if tmp[0].isnumeric():
                read = False
                rowsToSkip = i
            else:
                i = i+1
    f.close()
    
    # Load data as numpy array
    data= loadtxt(FilePath, delimiter=",",skiprows=rowsToSkip)
    return data

def buildDataDictionary(fileDir):
    # Read all the exported file and create a data structure based on nested
    # dictionaries. 
    
    # Get the file list
    fileList = [f for f in listdir(fileDir) if isfile(join(fileDir, f)) 
                        and not(f.find('_') == -1)]
    
    # IMPORTANT: for the future updates it is mandatory to iterate through 
    # the sensor's names
    SensorName = "AI 1"
    # Build KPI dictionary
    KPIdict = {"Time": {},
               "Frequency": {}}
    
    for f in fileList:
        try:
            data = getData(f)
            statName = f[f.find("_")+1:f.find(".")].replace(" ","_")
            timeDict = {"Dt": round((data[1,0]-data[0,0])*1000,2),
                        "data": data[:,1].tolist()}
            KPIdict["Time"][statName] = timeDict
        except:
            print("Impossible to retrieve data from " + f)
    
    # Build sensor dictionary
    # Get the sensor data from the csv table
    try:
        SensorTable = read_csv("SensorTable.csv")
        sensorSpec = SensorTable.query("Dewe_name == "+ '"'+SensorName+'"')
        sensorDict = {SensorName: {
                      "MOD": sensorSpec["MOD"].to_string(index = False).replace(' ',''),
                      "MAC": sensorSpec["MAC"].to_string(index = False).replace(' ',''),
                      "LOC": sensorSpec["LOC"].to_string(index = False).replace(' ',''),
                      "KPI": KPIdict
                      }
            }
    except KeyError:
        print("Sensor not present in the table")
        sensorDict = {}
        sensorDict["KPI"] = KPIdict
    except FileNotFoundError:
        print("Make sure the sensor table file and the python script are in the same directory")
        sensorDict = {}
        sensorDict["KPI"] = KPIdict
    
    FilePath = join(fileDir,fileList[0])
    metaDataFile = getMetadata(FilePath)
    
    # Build main dictionary
    dt = datetime.strptime(metaDataFile["Start time"], '%m/%d/%Y %H:%M:%S.%f')
    delta = timedelta(milliseconds=int(metaDataFile["Post time"]))
    endTime = dt+delta
    endTimeString = str(endTime.month) + '/' + str(endTime.day) + '/' + \
                    str(endTime.year) + ' ' + str(endTime.hour) + ':' + \
                    str(endTime.minute) + ':' + str(endTime.second) + '.' +\
                    str(endTime.microsecond)[0:-3]
    dataDict = {
                "DV": sensorSpec["DV"].to_string(index = False).replace(' ',''),
                "DAQ": sensorSpec["DAQ"].to_string(index = False).replace(' ',''),
                "MU": "m/s2",
                "S": sensorDict,
                "AST": metaDataFile["Start time"],
                "AET": endTimeString,
                "SF": metaDataFile["Sample rate"],
                "PT": metaDataFile["Post time"],
        }
    return dataDict

def buildRawDictionary(fileDir):
    # Build the dictionary based data structure, see buildDataDictionary().
    
    # IMPORTANT: for the future updates it is mandatory to iterate through 
    # the sensor's names
    SensorName = "AI 1"
    
    # Get the file list
    fileList = [f for f in listdir(fileDir) if isfile(join(fileDir, f)) 
                        and f.find('_') == -1 and not(f.find('.txt') == -1) ]
    
    try:
        FilePath = join(fileDir,fileList[0])
        data = getData(FilePath)
    except:
        print("Impossible to retrieve raw data")
    
    
    # Build sensor dictionary
    SensorTable = read_csv("SensorTable.csv")
    sensorSpec = SensorTable.query("Dewe_name == "+ '"'+SensorName+'"')
    sensorDict = {SensorName: {
                  "MOD": sensorSpec["MOD"].to_string(index = False).replace(' ',''),
                  "MAC": sensorSpec["MAC"].to_string(index = False).replace(' ',''),
                  "LOC": sensorSpec["LOC"].to_string(index = False).replace(' ',''),
                  "Data": data[:,1].tolist()
                  }
        }
    FilePath = join(fileDir,fileList[0])
    metaDataFile = getMetadata(FilePath)
    
    # Build main dictionary
    dt = datetime.strptime(metaDataFile["Start time"], '%m/%d/%Y %H:%M:%S.%f')
    delta = timedelta(milliseconds=int(metaDataFile["Post time"]))
    endTime = dt+delta
    endTimeString = str(endTime.month) + '/' + str(endTime.day) + '/' + \
                    str(endTime.year) + ' ' + str(endTime.hour) + ':' + \
                    str(endTime.minute) + ':' + str(endTime.second) + '.' +\
                    str(endTime.microsecond)[0:-3]
    dataDict = {
                "DV": sensorSpec["DV"].to_string(index = False).replace(' ',''),
                "DAQ": sensorSpec["DAQ"].to_string(index = False).replace(' ',''),
                "MU": "m/s2",
                "S": sensorDict,
                "AST": metaDataFile["Start time"],
                "AET": endTimeString,
                "SF": int(metaDataFile["Sample rate"]),
                "PT": int(metaDataFile["Post time"]),
        }
    return dataDict

def getShot(date):
    dt = datetime.strptime(date, '%m/%d/%Y %H:%M:%S.%f')
    y = str(dt.year)   
    if len(str(dt.month)) == 1:
       m = '0' + str(dt.month)
    else:
        m = str(dt.month)
    if len(str(dt.day)) == 1:
       d = '0' + str(dt.day)
    else:
        d = str(dt.day)
    if len(str(dt.hour)) == 1:
       h = '0' + str(dt.hour)
    else:
        h = str(dt.hour)
    if len(str(dt.minute)) == 1:
       mi = '0' + str(dt.minute)
    else:
        mi = str(dt.minute)
    if len(str(dt.second)) == 1:
       s = '0' + str(dt.second)
    else:
        s = str(dt.second)
    shot = y+m+d+h+mi+s
    return shot

def to_json(data, name):
    # Write the json file
    couchDir = "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\CouchDB"
    with open(couchDir + '\\' + name +'.json', 'w') as f:
        dump(data, f)
    f.close()
    
def to_couchDB():
    with open("NewConfig.txt") as f:
        config = load(f)
    f.close()
    
    dataDir = "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\Scripts\\AutomationData"
    folderList = [f for f in listdir(dataDir) if isdir(join(dataDir, f))]
    
    for f in folderList:
        path = join(dataDir,f)
        dataDict = buildDataDictionary(path)
        rawDict = buildRawDictionary(path)
    
        shot = getShot(dataDict["AST"])
        print("Uploading shot: " + shot)
        dataDictName = shot + "KPI"
        rawDictName = shot + "Raw"
        to_json(dataDict, dataDictName)
        to_json(rawDict, rawDictName)