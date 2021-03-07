from os import listdir, remove
from shutil import rmtree
from os.path import isfile, isdir, join, realpath, dirname
from json import load
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS

import autoUtils as au 

# Connection setup 
def statToInflux(fileList, write_api, Config, fileDir,fDate):
    measurement = Config["Measurement"]
    org         = Config["org"]
    bucket      = Config["bucket"]
    sensorName  = "AI_1"
    
    sampleRate  = au.getSampleRate(sensorName.replace("_", " "), fileDir)
    
    for i in range(len(fileList)):
        # Get the field name
        start = fileList[i].find('_') + 1
        end = fileList[i].find('.')
        
        field = fileList[i][start:end]
        
        tags = [
            "data=stat",
            "Machine=Motor1",
            "SampleRate="+str(sampleRate),
            "Shot="+fDate,
            "Sensor="+sensorName
            ]
        
        fileName = join(fileDir,fileList[i])
        
        # Convert to line protocol
        LPfile = au.buildLP(measurement,tags, field, fileName)
    
        print("Writing: " + field)
        write_api.write(bucket, org, LPfile)

def rawToInflux(Config, write_api, fileDir, fDate):
    # Load RawData
    measurement = Config["Measurement"]
    org         = Config["org"]
    RawBucket   = Config["RawBucket"]
    
    sensorName  = "AI_1"
    sampleRate  = au.getSampleRate(sensorName.replace("_", " "), fileDir)
    
    tags = [
            "data=Raw",
            "Machine=Motor1",
            "SampleRate="+str(sampleRate),
            "Shot="+fDate,
            "Sensor="+sensorName
            ]
    
    field = "acceleration"
    
    fileName = join(fileDir,sensorName.replace('_', ' ')+".txt")
    LPfile = au.buildLP(measurement,tags, field, fileName)
    
    print("Writing raw data")
    write_api.write(RawBucket, org, LPfile)
    print("Done.")
    
def getFolderDate(folder):
    for i in range(len(folder)):
        if folder[i].isnumeric() == True:
            fDate = folder[i:]
            break
    return fDate

def uploadData():
    deleteWhenDone = True
    mypath = dirname(realpath(__file__))
    # Read data
    try: 
        ConfigFile = open(join(mypath,'Config.json'))
        Config = load(ConfigFile)
        ConfigFile.close()
    except:
        print("Can't open the configuration file.")
        
    dataDir     = Config["DataDir"]
    token       = Config["token"]
    clientURL   = Config["clientURL"]
    
    folderList = [f for f in listdir(dataDir) if isdir(join(dataDir, f))]
    
    client = InfluxDBClient(url=clientURL, token=token)
    write_api = client.write_api(write_options=ASYNCHRONOUS)
    
    for i in range(len(folderList)):
        print("loading folder: " + folderList[i])
        fileDir = join(dataDir,folderList[i])
        fileList = [f for f in listdir(fileDir) if isfile(join(fileDir, f)) 
                    and not(f.find('_') == -1)]
        
        fDate = getFolderDate(folderList[i])
        statToInflux(fileList, write_api, Config, fileDir, fDate)
        rawToInflux(Config, write_api, fileDir, fDate)
        
        if deleteWhenDone:
            rmtree(join(dataDir,folderList[i]))
            try:
                remove(join(dataDir,folderList[i] + '.dxd'))
            except:
                print('It is not possible to remove the file')
                pass