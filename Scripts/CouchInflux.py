import requests
import pandas as pd
from influxdb_client import InfluxDBClient, BucketsApi, OrganizationsApi
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import configparser
from influxdb_client.client.write_api import ASYNCHRONOUS
from urllib.request import urlopen

def test_connection(client, bucket_name, org_name, host):
    ''' Test connection avaliability with Influx and CouchDB
        host[0]: Influx URL
        host[1]: Couch URL
    '''
    
    influx_avaliable = connection_avaliable(host=host[0], 
                                    host_name="InfluxDB")
    couch_avaliable = connection_avaliable(host=host[1], 
                                    host_name="CouchDB")
    
    if not influx_avaliable or not couch_avaliable: return
    
    # Test organization and bucket existence in influxDB
    buckets_client = BucketsApi(client)
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

    if not (org_name in org_names):
        print("Org doesn't exist")
        return False

    if not (bucket_name in bucket_names):
        print("Bucket doesn't exist")
        return False

    return True


def upload_history_table(new_file_name):
    ht = pd.read_csv("history_table.csv")

    # Check if the file has already been loaded on couchDB
    query = ht[(ht["file_name"] == new_file_name) & (ht["influx_db"] == False)]
    if not query.empty:
        row_index = query.index[0]
        ht.loc[row_index, "influx_db"] = True
        ht.to_csv("history_table.csv", index=False)
    else:
        print("Error")
        print(new_file_name + " already uploaded to influxDB")


def get_file_to_load():
    ''' Get the files to load on influx based on hystory table '''
    
    file_to_load = []
    ht = pd.read_csv("history_table.csv")

    # # Check if the file has already been loaded on couchDB
    query = ht[(ht["influx_db"] == False) & 
               (ht["file_name"].str.contains("KPI"))]
    file_to_load = query["file_name"].to_list()
    
    print(str(len(file_to_load)) + " files to load")
    return file_to_load


def generate_lines(data_file, config):

    sensorList = list(data_file["S"].keys())
    time_KPI_list = list(data_file["S"][sensorList[0]]["KPI"]["Time"].keys())
    FreqKPIList = list(data_file["S"][sensorList[0]]["KPI"]["Frequency"].keys())

    measurement = config["INFLUXDB"]["measurement"]

    # If the KPI list are empty no data were acquired
    if time_KPI_list == [] and FreqKPIList == []:
        print("No data were acquired")
        return None

    # Get timestamp - format ISO 8601
    date = datetime.strptime(data_file["AST"], "%Y-%m-%dT%H:%M:%S.%f")

    # Iterate on Time - KPI
    data_points = []
    for i in range(len(time_KPI_list)):
        dt = data_file["S"][sensorList[0]]["KPI"]["Time"][time_KPI_list[i]][
            "Dt"
        ]  # [ms]

        # Build the tag string
        shot = data_file["_id"].split("-")[1]
        tag_string = (
            "Sample_rate="
            + str(data_file["SF"])
            + ","
            + "Shot="
            + shot
            + ","
            + "Sensor="
            + sensorList[0].replace(" ", "_")
            + ","
            + "Machine="
            + data_file["S"][sensorList[0]]["MAC"]
            + ","
            + "KPI_Type="
            + "Time"
        )

        data = data_file["S"][sensorList[0]]["KPI"]["Time"][time_KPI_list[i]]["data"]

        for d in range(len(data)):
            time_delta = timedelta(milliseconds=float(dt) * d)
            actual_time = date + time_delta
            data_points.append(
                measurement
                + ","
                + tag_string
                + " "
                + time_KPI_list[i]
                + "="
                + str(data[d])
                + " "
                + str(int(actual_time.timestamp() * 1e9))
            )

    return data_points

def connection_avaliable(host, host_name):
    try:
        urlopen(host, timeout=2)
        return True
    except Exception as e:
        print(host_name + " connection not avaliable")
        print(str(e))
        return False
    
def to_influx():
    print("\n------Influx Upload------")
    ConfigFile = "config.ini"
    config = configparser.ConfigParser()
    config.read(ConfigFile)
    
    host = [config["INFLUXDB"]["influxurl"],
            config["COUCHDB"]["couch_url"]]
    
    bucket_name = config["INFLUXDB"]["kpibucket"]
    org_name = config["INFLUXDB"]["org"]
    
    username = config["COUCHDB"]["username"]
    password = config["COUCHDB"]["password"]
    couch_db_url = config["COUCHDB"]["couch_url"] \
                + "/"+config["COUCHDB"]["database"]+"/"
                
    client = InfluxDBClient(
        url=host[0], token=config["INFLUXDB"]["token"]
    )

    write_client = client.write_api(write_options=ASYNCHRONOUS)
    if not test_connection(client, bucket_name, org_name, host): 
        return

    file_to_load = get_file_to_load()
    
    connection_lost = False
    for file in file_to_load:
        if connection_lost:
            print("Connection lost")
            return
        try:
            resp = requests.get(
                couch_db_url + file, auth=HTTPBasicAuth(username, password)
            )
        except Exception as e:
            print("File: " + file)
            print("Can't retrieve the data from CouchDB, an exception occurred")
            print("Exception: " + str(e))
            connection_lost = True
        else:
            if resp.status_code != 200:
                print(resp.text)
                print(
                    "Can't retrieve the data from CouchDB, status code: "
                    + str(resp.status_code)
                )
            else:
                print("Data retrieved from CouchDB")
                data_points = generate_lines(resp.json(), config)
                try:
                    write_client.write(bucket_name, org_name, data_points)
                except Exception as e:
                    print("Exception: " + str(e))
                    connection_lost = True
                else:
                    print(str(file) + " loaded successfully")
                    upload_history_table(file)
                    


if __name__ == "__main__":
    to_influx()
