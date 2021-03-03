from os import listdir, getcwd, remove
from shutil import rmtree
from os.path import isfile, isdir, join 
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS

import autoUtils as au 

# Connection setup 
def statToInflux(fileList):
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

def rawToInflux():
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

deleteWhenDone = True

datapath = join(getcwd(),'AutomationData')
folderList = [f for f in listdir(datapath) if isdir(join(datapath, f))]

measurement = 'LattePanda'
token       = "mytoken"
org         = "myorg"
bucket      = "Prova"
RawBucket   = 'Prova1'
sensorName  = "AI 1"

client = InfluxDBClient(url="http://localhost:8086", token=token)
write_api = client.write_api(write_options=ASYNCHRONOUS)

for i in range(len(folderList)):
    print("loading folder: " + folderList[i])
    mypath = join(getcwd(),'AutomationData',folderList[i])
    fileList = [f for f in listdir(mypath) if isfile(join(mypath, f)) and not(f.find('_') == -1)]
    statToInflux(fileList)
    rawToInflux()
    if deleteWhenDone:
        rmtree(join(getcwd(),'AutomationData',folderList[i]))
        try:
            remove(join(getcwd(),'AutomationData',folderList[i] + '.dxd'))
        except:
            print('It is not possible to remove the file')