from os import listdir, getcwd
from os.path import isfile, join 
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS

import autoUtils as au 

mypath = join(getcwd(),'AutomationData','LattePanda20210303162745')

fileList = [f for f in listdir(mypath) if isfile(join(mypath, f)) and not(f.find('_') == -1)]

measurement = 'LattePanda'

token       = "mytoken"
org         = "myorg"
bucket      = "NewBucket"
RawBucket   = 'RawBucket'
sensorName  = "AI 1"

# Connection setup 
client = InfluxDBClient(url="http://localhost:8086", token=token)
write_api = client.write_api(write_options=ASYNCHRONOUS)



for i in range(len(fileList)):
    # Get the field name
    start = fileList[i].find('_') + 1
    end = fileList[i].find('.')
    
    field = fileList[i][start:end]
    
    tags = [
        "data=stat",
        "Machine=Motor1",
        "Sensor=Acc1"
        ]
    
    fileName = join(mypath,fileList[i])
    
    # Convert to line protocol
    LPfile = au.buildLP(measurement,tags, field, fileName)

    
    print("Writing: " + field)
    write_api.write(bucket, org, LPfile)


# Load RawData
tags = [
        "data=Raw",
        "Machine=Motor1",
        "Sensor=Acc1"
        ]

field = "acceleration"

fileName = join(mypath,sensorName+".txt")
LPfile = au.buildLP(measurement,tags, field, fileName)

    
print("Writing raw data")
write_api.write(RawBucket, org, LPfile)
print("Done.")