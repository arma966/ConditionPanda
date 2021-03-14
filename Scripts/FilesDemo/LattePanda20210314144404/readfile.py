import numpy as np
import json

def getMetadata(FileName):
    dictionary =  {}
    read = True
    with open(FileName) as f:
        while read:
            tmp = f.readline()
            if not(tmp == "\n"):
                if not(tmp.find(":") == -1):
                    s = tmp.strip().split(": ",maxsplit = 1)
                    dictionary[s[0]] = s[1]
            else:
                read = False
    f.close()
    return dictionary

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
    data= np.loadtxt(FileName, delimiter=",",skiprows=rowsToSkip)
    return data

readable = True
FileName = "AI 1_MIN.txt"

metaDataFile = getMetadata(FileName)


data = getData(FileName)

sensorList = {"AI 1": {
              "Model": "J352SN",
              "Machine": "MotorA",
              "Place": "Rotor",
              "Stat": {"MAX": {
                  "dt": round((data[1,0]-data[0,0])*1000),
                  "data": data[:,1].tolist(),
                  "MU": "m/s2"
                  },
                "MIN": {
                  "dt": round((data[1,0]-data[0,0])*1000),
                  "data": data[:,1].tolist(),
                  "MU": "m/s2"
                  }
                  }
              }
    }

dataDict = {
            "DV": "LattePanda",
            "DAQ": "IOLITEd-1xACC",
            "S": sensorList,
            "AST": metaDataFile["Start time"],
            "AET": metaDataFile["Start time"],
            "SF": metaDataFile["Sample rate"],
            "PT": metaDataFile["Post time"],
    }


with open('prova.json', 'w') as f:
    if readable:
        json.dump(dataDict, f, indent = 4)
    else:
        json.dump(dataDict, f)
f.close()



