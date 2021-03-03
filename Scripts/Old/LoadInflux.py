# Dataset di prova

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS

import autoUtils as au

# Variable definition
fileName = '.\\AutomationData\\MeasureName\\AI 1_MAX.txt'

measurement = 'LattePanda'

tags = [
    "data=stat",
    "Machine=Motor1",
    "Sensor=Acc"
    ]

fields      = 'max'

token       = "mytoken"
org         = "myorg"
bucket      = "NewBucket"


# Convert txt file into line protocol format
try:
    LPfile = au.buildLP(measurement,tags, fields, fileName)
    print("Data converted successfully")
except:
    print("Data not converted, check the file format")


# Loading data to influx
# Warning: if data are not loaded, the API doesn't rise exceptions

client = InfluxDBClient(url="http://localhost:8086", token=token)

write_api = client.write_api(write_options=ASYNCHRONOUS)

print("writing")
write_api.write(bucket, org, LPfile)
print("finish")