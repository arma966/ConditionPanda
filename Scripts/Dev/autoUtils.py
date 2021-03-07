import re
import datetime
from numpy import loadtxt
from os.path import join

def getTimestamp(fileName):
    with open(fileName,'r') as myfile:
        data = myfile.read(192)
    myfile.close()
    
    start = [i.start() for i in re.finditer("Start time", data)][0]
    date = data[start+12:start+34]
   
    if date.find('/') == 1:
        # mo:1
        mo = int(date[0:1])
        if date[2:].find('/') == 1:
            # mo:1 dd:1
            dd = int(date[2:3])
            yy = int(date[4:8])
            hh = int(date[9:11])
            mi = int(date[12:14])
            ss = int(date[15:17])
            us = int(date[18:21])*1000
        else:
            # mo:1 dd:2
            dd = int(date[2:3+1])
            yy = int(date[4+1:8+1])
            hh = int(date[9+1:11+1])
            mi = int(date[12+1:14+1])
            ss = int(date[15+1:17+1])
            us = int(date[18+1:21+1])*1000
    else:
        # mo:2 
        mo = int(date[0:2])
        if date[3:].find('/') == 1:
            # mo:2 dd:1
            dd = int(date[2+1:3+1])
            yy = int(date[4+1:8+1])
            hh = int(date[9+1:11+1])
            mi = int(date[12+1:14+1])
            ss = int(date[15+1:17+1])
            us = int(date[18+1:21+1])*1000
        else:
            # mo:2 dd:2
            dd = int(date[2+1:3+2])
            yy = int(date[4+2:8+2])
            hh = int(date[9+2:11+2])
            mi = int(date[12+2:14+2])
            ss = int(date[15+2:17+2])
            us = int(date[18+2:21+2])*1000

    # y m d h min s 
    timestamp = datetime.datetime(yy,mo,dd,hh,mi,ss,us).timestamp()
    
    return timestamp

def getSampleRate(sensorName, Dir):
    file2open = join(Dir,sensorName + '.txt')
    with open(file2open) as f:
        file = f.readlines(250)
    f.close()
    for line in file:
        if line.find("Sample rate") == 0:
            SampleRate = int(line[13:-1])
    return SampleRate

def buildLP(measurement, tags, fields, fileName):
    tagString = ""
    for i in range(len(tags)):
        tagString = tagString+tags[i]
        if i < len(tags)-1:
            tagString = tagString + ","
    # Get timestamp 
    timestamp = int(getTimestamp(fileName)*1e9)
    try:
        data = loadtxt(fileName, skiprows=11, delimiter=',')
    except:
        data = loadtxt(fileName, skiprows=12, delimiter=',')
    lines = [measurement
          + ","+tagString
          + " "
          + fields + "=" + str(data[d,1]) + " "
          + str(timestamp + int(data[d,0]*1e9)) for d in range(len(data[:,0]))]
    return lines