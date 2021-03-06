import requests
from re import findall 
from json import load 
from influxdb_client.client.util.date_utils_pandas import PandasDateTimeHelper
import pandas as pd
from influxdb_client import InfluxDBClient, WriteOptions,BucketsApi,OrganizationsApi
import sys
from requests.auth import HTTPBasicAuth

def test_influx_connection(bucket_name, org_name):
    buckets_client= BucketsApi(client)
    bucket_names = []
    bucket_obj = buckets_client.find_buckets().to_dict()
    for i in bucket_obj["buckets"]:
        if i["name"][0] != "_":
            bucket_names.append(i["name"])
           
    org_names = []
    org_client = OrganizationsApi(client)
    org_obj = org_client.find_organizations()
    for i in range(len(org_obj)):
        org_names.append(org_obj[i].name)
        
    if not(org_name in org_names):
        print("Org doesn't exist")
        return False
        
    if not(bucket_name in bucket_names):
        print("Bucket doesn't exist")
        return False
    
    return True

def get_file_to_load():
    file_to_load = []
    ht = pd.read_csv("history_table.csv")

    # # Check if the file has already been loaded on couchDB
    query = ht[(ht["influx_db"] == False) & (ht["file_name"].str.contains("KPI"))]
    file_to_load = query["file_name"].to_list()
    return file_to_load
        
def fileToInflux(content):

    sensorList = list(content["S"].keys())
    time_KPI_list = list(content["S"][sensorList[0]]["KPI"]["Time"].keys())
    FreqKPIList = list(content["S"][sensorList[0]]["KPI"]["Frequency"].keys())

    measurement = "batch_meas"

    # If the KPI list are empty no data were acquired
    if time_KPI_list == [] and FreqKPIList == []:
        print("No data were acquired")
        return None
    
    # Get timestamp - format ISO 8601    
    date = pd.to_datetime(content["AST"], format='%Y-%m-%dT%H:%M:%S.%f', errors='ignore')
    
    # Iterate on Time - KPI
    data_points = []
    for i in range(len(time_KPI_list)):
        dt = content["S"][sensorList[0]]["KPI"]["Time"][time_KPI_list[i]]["Dt"] # [ms]
        
        # Build the tag string
        shot = content["_id"].split('-')[1]
        tag_dict = {"Sample_rate": str(content["SF"]),
                    "Shot": shot,
                    "Sensor": sensorList[0].replace(" ","_"),
                    "Machine": content["S"][sensorList[0]]["MAC"],
                    "KPI_Type": 'Time'}

        
        data = content["S"][sensorList[0]]["KPI"]["Time"][time_KPI_list[i]]["data"]
        
        for d in range(len(data)):
            time_delta = pd.to_timedelta(float(dt)*d,unit = 'ms')
            actual_time = date + time_delta
            fields = {time_KPI_list[i]: data[d]}
            data_points.append({"measurement": measurement,
                                "tags": tag_dict,
                                "fields": fields,
                                "time": actual_time.isoformat()})
    return data_points
        
        
url = "http://localhost:8086"
client = InfluxDBClient(url=url,
                            token="mytoken")
bucket_name = "KPI_db"
org_name = "myorg"

write_client = client.write_api(write_options=WriteOptions(batch_size=5000,
                                                             flush_interval=10_000,
                                                             jitter_interval=2_000,
                                                             retry_interval=5_000,
                                                             max_retries=5,
                                                             max_retry_delay=30_000,
                                                             exponential_base=2))

if not test_influx_connection(bucket_name, org_name): sys.exit()

file_to_load = get_file_to_load()
username = "LattepandaCouch"
password = "peanut96"
couch_url = "http://192.168.1.5:5984/students/"

for file in file_to_load:
    try:
            resp = requests.get(couch_url + file,
                                auth=HTTPBasicAuth(username, password))
    except Exception as e:
        print("Can't retrieve the data from CouchDB, an exception occurred")
        print("Exception: " + str(e))
    else:
        if resp.status_code != 200:
            print(resp.text)
            print("Can't retrieve the data from CouchDB, status code: " \
                  + str(resp.status_code))
        else:
            print("Data retrieved from CouchDB")
            data_points = fileToInflux(resp.json())
    try:
        write_client.write(bucket_name, org_name, data_points)
    except Exception as e:
        print("Exceptio: " + str(e))
    else:
        print(str(file) + " loaded successfully")
    # Update history table
    

