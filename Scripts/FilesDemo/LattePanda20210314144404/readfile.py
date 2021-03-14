from numpy import loadtxt
from json import dump 
from os import listdir
from os.path import join, isfile
from datetime import datetime, timedelta

def getMetadata(FileName):
    metaDictionary =  {}
    read = True
    with open(FileName) as f:
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

def getData(FileName):
    # get the number of rows to skip
    read = True
    with open(FileName) as f:
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
    data= loadtxt(FileName, delimiter=",",skiprows=rowsToSkip)
    return data

def buildDataDictionary(fileDir):
    # Get the file list
    fileList = [f for f in listdir(fileDir) if isfile(join(fileDir, f)) 
                        and not(f.find('_') == -1)]
    
    # Build KPI dictionary
    KPIdict = {}
    for f in fileList:
        try:
            data = getData(f)
            statName = f[f.find("_")+1:f.find(".")].replace(" ","_")
            statDict = {"Dt": round((data[1,0]-data[0,0])*1000),
                        "data": data[:,1].tolist()}
            KPIdict[statName] = statDict
        except:
            print("Impossible to retrieve data from " + f)
    
    # Build sensor dictionary
    sensorDict = {"AI 1": {
                  "MOD": "J352SN",
                  "MAC": "MotorA",
                  "LOC": "Rotor",
                  "KPI": KPIdict
                  }
        }
    
    metaDataFile = getMetadata(fileList[0])
    
    # Build main dictionary
    dt = datetime.strptime(metaDataFile["Start time"], '%m/%d/%Y %H:%M:%S.%f')
    delta = timedelta(milliseconds=int(metaDataFile["Post time"]))
    endTime = dt+delta
    endTimeString = str(endTime.month) + '/' + str(endTime.day) + '/' + \
                    str(endTime.year) + ' ' + str(endTime.hour) + ':' + \
                    str(endTime.minute) + ':' + str(endTime.second) + '.' +\
                    str(endTime.microsecond)[0:-3]
    dataDict = {
                "DV": "LattePanda",
                "DAQ": "IOLITEd-1xACC",
                "MU": "m/s2",
                "S": sensorDict,
                "AST": metaDataFile["Start time"],
                "AET": endTimeString,
                "SF": metaDataFile["Sample rate"],
                "PT": metaDataFile["Post time"],
        }
    return dataDict

def buildRawDictionary(fileDir):
    # Get the file list
    fileList = [f for f in listdir(fileDir) if isfile(join(fileDir, f)) 
                        and f.find('_') == -1 and not(f.find('.txt') == -1) ]
    
    try:
        data = getData(fileList[0])
    except:
        print("Impossible to retrieve raw data")
    
    
    # Build sensor dictionary
    sensorDict = {"AI 1": {
                  "MOD": "J352SN",
                  "MAC": "MotorA",
                  "LOC": "Rotor",
                  "Data": data[:,1].tolist()
                  }
        }
    
    metaDataFile = getMetadata(fileList[0])
    
    # Build main dictionary
    dt = datetime.strptime(metaDataFile["Start time"], '%m/%d/%Y %H:%M:%S.%f')
    delta = timedelta(milliseconds=int(metaDataFile["Post time"]))
    endTime = dt+delta
    endTimeString = str(endTime.month) + '/' + str(endTime.day) + '/' + \
                    str(endTime.year) + ' ' + str(endTime.hour) + ':' + \
                    str(endTime.minute) + ':' + str(endTime.second) + '.' +\
                    str(endTime.microsecond)[0:-3]
    dataDict = {
                "DV": "LattePanda",
                "DAQ": "IOLITEd-1xACC",
                "MU": "m/s2",
                "S": sensorDict,
                "AST": metaDataFile["Start time"],
                "AET": endTimeString,
                "SF": metaDataFile["Sample rate"],
                "PT": metaDataFile["Post time"],
        }
    return dataDict

def to_json(data, name):
    # Write the json file
    with open(name +'.json', 'w') as f:
        dump(data, f)
    f.close()

fileDir = "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\Scripts\\FilesDemo\\LattePanda20210314144404"

dataDict = buildDataDictionary(fileDir)
rawDict = buildRawDictionary(fileDir)

dt = datetime.strptime(dataDict["AST"], '%m/%d/%Y %H:%M:%S.%f')

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
timestampName = y+m+d+h+mi+s

dataDictName = timestampName + "Math"
rawDictName = timestampName + "Raw"
to_json(dataDict, dataDictName)
to_json(rawDict, rawDictName)