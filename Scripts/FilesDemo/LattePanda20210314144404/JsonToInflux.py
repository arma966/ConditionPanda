# Line protocol 
#
# Syntax
# <measurement>[,<tag_key>=<tag_value>[,<tag_key>=<tag_value>]] <field_key>=<field_value>[,<field_key>=<field_value>] [<timestamp>]
#
# Example
# myMeasurement,tag1=value1,tag2=value2 fieldKey="fieldValue" 1556813561098000000

import json 
from re import findall
from datetime import datetime
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS

def openJson(FileName):
    try:
        with open(FileName) as f:
            content = json.load(f)
        return content
    except FileNotFoundError:
        print("File not found")
    else:
        f.close()
def KPIto_influx(FileName):
    with open("NewConfig.json") as f:
        config = json.load(f)
    f.close()
    
    
    client = InfluxDBClient(url=config["InfluxDB"]["Client URL"], 
                            token=config["InfluxDB"]["Token"])
    bucket = config["InfluxDB"]["KPI Bucket"]
    org = config["InfluxDB"]["Org"]
    
    write_api = client.write_api(write_options=ASYNCHRONOUS)
    
    content = openJson(FileName)
    SentFiles = {}
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
        tagString = "Sample_rate=" + str(content["SF"]) +","+\
                    "Shot="+ list(findall("\d+",FileName))[0] +","+\
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
        SentFiles[TimeKPIList[i]] = lines
    
    # Iterate on Frequency - KPI
    for i in range(len(FreqKPIList)): 
        # Build the tag string
        tagString = "Sample_rate=" + str(content["SF"]) +","+\
                    "Shot="+ list(findall("\d+",FileName))[0] +","+\
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
        SentFiles[TimeKPIList[i]] = lines
    return SentFiles
    

FileName = "20210314144406KPI.json"

sent = KPIto_influx(FileName)
