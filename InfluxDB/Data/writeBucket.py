from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "mytoken"
org = "myorg"
bucket = "mybucket"

client = InfluxDBClient(url="http://localhost:8086", token=token)

write_api = client.write_api(write_options=SYNCHRONOUS)

with open("test3_linep", "r") as file:
	lines = file.readlines()

file.close()
print("writing")
write_api.write(bucket, org, lines)
print("finish")