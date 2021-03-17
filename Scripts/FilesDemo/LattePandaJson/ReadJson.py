import numpy as np
import json 

def getMetadata(FileName):
    content = ""
    read = True
    with open(FileName) as f:
        while read:
            tmp = f.readline()
            if not(tmp == "\n"):
                content = content + tmp
            else:
                read = False
    f.close()
    return content

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


FileName = "AI 1_MIN.json"

with open(FileName) as f: 
    obj = json.load(f)
f.close()