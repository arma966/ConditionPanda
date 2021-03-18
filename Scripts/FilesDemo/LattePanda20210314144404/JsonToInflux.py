# Line protocol 
#
# Syntax
# <measurement>[,<tag_key>=<tag_value>[,<tag_key>=<tag_value>]] <field_key>=<field_value>[,<field_key>=<field_value>] [<timestamp>]
#
# Example
# myMeasurement,tag1=value1,tag2=value2 fieldKey="fieldValue" 1556813561098000000

import json 
from re import findall
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS
from os import listdir
from os.path import join, isfile, exists
import sys

def openJson(FilePath):
    try:
        with open(FilePath) as f:
            content = json.load(f)
        return content
    except FileNotFoundError:
        print("File not found")
    else:
        f.close()
def fileToInflux(FilePath):
    with open("NewConfig.json") as f:
        config = json.load(f)
    f.close()
    
    
    client = InfluxDBClient(url=config["InfluxDB"]["Client URL"], 
                            token=config["InfluxDB"]["Token"])
    bucket = config["InfluxDB"]["KPI Bucket"]
    org = config["InfluxDB"]["Org"]
    
    write_api = client.write_api(write_options=ASYNCHRONOUS)
    
    print("Loading to influx: " + FilePath)
    
    content = openJson(FilePath)
    SentLines = {}
    sensorList = list(content["S"].keys())
    TimeKPIList = list(content["S"][sensorList[0]]["KPI"]["Time"].keys())
    FreqKPIList = list(content["S"][sensorList[0]]["KPI"]["Frequency"].keys())
    measurement = "meas"
    
    # Get timestamp 
    date = datetime.strptime(content["AST"], '%m/%d/%Y %H:%M:%S.%f')
    timestamp = int(datetime.timestamp(date) * 1e9)
    
    # Iterate on Time - KPI
    for i in range(len(TimeKPIList)): 
        # Build the tag string
        shot = list(findall("\d+",FilePath.split("\\")[-1]))[0]
        tagString = "Sample_rate=" + str(content["SF"]) +","+\
                    "Shot="+ shot +","+\
                    "Sensor="+ sensorList[0].replace(" ","_") +","+\
                    "Machine="+ content["S"][sensorList[0]]["MAC"] +","+\
                    "KPI_Type="+ 'Time'
                    
        fields = TimeKPIList[i]
        data = content["S"][sensorList[0]]["KPI"]["Time"][TimeKPIList[i]]["data"]
        dt = content["S"][sensorList[0]]["KPI"]["Time"][TimeKPIList[i]]["Dt"] # [ms]
        
        lines = [measurement
                  + ","+tagString
                  + " "
                  + fields + "=" + str(data[d]) + " "
                  + str(timestamp+int(d*dt*1e6)) for d in range(len(data))]
        
        # Send to influx
        print("Writing: " + fields)
        write_api.write(bucket, org, lines)
        SentLines[TimeKPIList[i]] = lines
    writeLog("Log.txt",shot + "KPI")
    
    # Iterate on Frequency - KPI
    for i in range(len(FreqKPIList)): 
        # Build the tag string
        shot = list(findall("\d+",FilePath.split("\\")[-1]))[0]
        tagString = "Sample_rate=" + str(content["SF"]) +","+\
                    "Shot="+ shot +","+\
                    "Sensor="+ sensorList[0].replace(" ","_") +","+\
                    "Machine="+ content["S"][sensorList[0]]["MAC"] +","+\
                    "KPI_Type="+ 'Time'
                    
        fields = TimeKPIList[i]
        data = content["S"][sensorList[0]]["KPI"]["Frequency"][FreqKPIList[i]]["data"]
        dt = content["S"][sensorList[0]]["KPI"]["Time"][FreqKPIList[i]]["Dt"] # [ms]
        
        lines = [measurement
                  + ","+tagString
                  + " "
                  + fields + "=" + str(data[d]) + " "
                  + str(timestamp+int(d*dt*1e6)) for d in range(len(data))]
        
        # Send to influx
        SentLines[TimeKPIList[i]] = lines
    writeLog("Log.txt",shot + "RAW")
    
def writeLog(logPath, shot):
    with open(logPath,'r') as f:
        logContent = f.readlines()
    with open(logPath,'a') as f:
        if shot + "\n" in logContent:
            print(shot + " already updated")
        else:
            f.write("ciao\n")
    f.close()

        
couchDir = "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\CouchDB"
daysBack = 2
fromDate = datetime.now() - timedelta(days = daysBack)

fileDir = join(couchDir,str(fromDate.year),str(fromDate.month),str(fromDate.day))
if not(exists(fileDir)):
    print("No data avaliable in date: " + str(fromDate))
    sys.exit()
    
fileList = [f for f in listdir(fileDir) if isfile(join(fileDir, f)) 
            and not(f.find('.json') == -1) and not(f.find('KPI') == -1)]
for f in fileList:
    FilePath = join(fileDir,f)
    fileToInflux(FilePath)
