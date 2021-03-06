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
from os import listdir
from os.path import join, isfile, exists
import configparser
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd

def open_json(FilePath):
    try:
        with open(FilePath) as f:
            content = json.load(f)
        return content
    except FileNotFoundError:
        print("[open_json()] File not found: " + FilePath)
    else:
        f.close()

def read_txt(file_path):
    try:
        with open(file_path) as f:
            content = f.readlines()
    except FileNotFoundError:
        print("[open txt] File not found: " + file_path)
        return None
    else:
        f.close()
        return content

def fileToInflux(FilePath, client, write_api, config):
    bucket = config["INFLUXDB"]["KPIbucket"]
    org = config["INFLUXDB"]["org"]

    print("Loading to influx: " + FilePath)

    content = open_json(FilePath)
    # SentLines = {}
    sensorList = list(content["S"].keys())
    time_KPI_list = list(content["S"][sensorList[0]]["KPI"]["Time"].keys())
    FreqKPIList = list(content["S"][sensorList[0]]["KPI"]["Frequency"].keys())

    AAA = 0 # Integrate measurement with config file
    measurement = "meas"

    # If the KPI list are empty no data were acquired
    if time_KPI_list == [] and FreqKPIList == []:
        print("No data were acquired")
        return None
    # Get timestamp - format ISO 8601
    date = datetime.strptime(content["AST"], '%Y-%m-%dT%H:%M:%S.%f')
    timestamp = int(datetime.timestamp(date) * 1e9)

    # Iterate on Time - KPI
    for i in range(len(time_KPI_list)):
        # Build the tag string
        shot = list(findall("\d+",FilePath.split("\\")[-1]))[0]
        tag_string = "Sample_rate=" + str(content["SF"]) +"," \
                      + "Shot="+ shot +"," \
                      + "Sensor="+ sensorList[0].replace(" ","_") +"," \
                      + "Machine="+ content["S"][sensorList[0]]["MAC"] +"," \
                      + "KPI_Type="+ 'Time'

        fields = time_KPI_list[i]
        data = content["S"][sensorList[0]]["KPI"]["Time"][time_KPI_list[i]]["data"]
        dt = content["S"][sensorList[0]]["KPI"]["Time"][time_KPI_list[i]]["Dt"] # [ms]

        lines = [measurement
                  + ","+tag_string
                  + " "
                  + fields + "=" + str(data[d]) + " "
                  + str(timestamp+int(d*dt*1e6)) for d in range(len(data))]

        # Send to influx
        result = write_api.write(bucket, org, lines)
        print("Writing: " + fields)
        if result != None:
            print("Something went wrong")
            print("write_api result: " + str(result))
        # SentLines[time_KPI_list[i]] = lines

    write_log(config["INFLUXDB"]["log_dir"],shot + "KPI")

    # Iterate on Frequency - KPI
    for i in range(len(FreqKPIList)):
        # Build the tag string
        shot = list(findall("\d+",FilePath.split("\\")[-1]))[0]
        tag_string = "Sample_rate=" + str(content["SF"]) +","+\
                    "Shot="+ shot +","+\
                    "Sensor="+ sensorList[0].replace(" ","_") +","+\
                    "Machine="+ content["S"][sensorList[0]]["MAC"] +","+\
                    "KPI_Type="+ 'Time'

        fields = time_KPI_list[i]
        data = content["S"][sensorList[0]]["KPI"]["Frequency"][FreqKPIList[i]]["data"]
        dt = content["S"][sensorList[0]]["KPI"]["Time"][FreqKPIList[i]]["Dt"] # [ms]

        lines = [measurement
                  + ","+tag_string
                  + " "
                  + fields + "=" + str(data[d]) + " "
                  + str(timestamp+int(d*dt*1e6)) for d in range(len(data))]

        # Send to influx
        # SentLines[time_KPI_list[i]] = lines


def write_log(log_path, file_name):
    try:
        with open(log_path,'a') as f:
                f.write(file_name +"\n")
    except FileNotFoundError:
        print("[write_log()] Log file doesn't exist")
    else:
        f.close()


def bucket_exists(client, config):
    response = False
    buckets_dir = client.buckets_api().find_buckets().to_dict()
    for i in range(len(buckets_dir["buckets"])):
        if buckets_dir["buckets"][i]["name"] == config["INFLUXDB"]["KPIbucket"]:
            response = True
            return response


def connection_avaliable(url):
    import socket
    from re import split

    influx_ip = split('//|:',url)[2]
    port = split('//|:',url)[3]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((influx_ip,int(port)))
    if result == 0:
        return True
    else:
        print("[connection_avaliable()] Can't connect to influxDB on")
        print("ip: " + influx_ip)
        print("port: " + port)
        return False
    sock.close()


def to_influx1(date_string):
    # Read the configuration file to obtain the log file path
    ConfigFile = "config.ini"
    config = configparser.ConfigParser()
    config.read(ConfigFile)

    url=config["INFLUXDB"]["influxurl"]
    if not connection_avaliable(url): return

    client = InfluxDBClient(url=url,
                            token=config["INFLUXDB"]["token"])

    if not bucket_exists(client, config):
        print("The bucket doesn't exist")
        return
    write_api = client.write_api(write_options=ASYNCHRONOUS)

    log_path = config["INFLUXDB"]["log_dir"]
    couch_dir = config["COUCHDB"]["couch_dir"]

    date = datetime.strptime(date_string, "%Y-%m-%d")

    # Build the file path from the given date
    couch_file_dir = join(couch_dir,str(date.year),str(date.month),str(date.day))
    if not(exists(couch_file_dir)):
        print("No data avaliable in date - Folder doesn't exist': " + str(date.date()))
        return
    else:
        if listdir(couch_file_dir) == []:
            print("No data avaliable in date: " + str(date.date()))
            return

    couch_file_list = [f for f in listdir(couch_file_dir) \
                       if isfile(join(couch_file_dir, f)) \
                       and not(f.find('.json') == -1) \
                       and not(f.find('KPI') == -1)]

    # For every measure in a day, check if it must be loaded, if yes load to
    # influx

    for f in couch_file_list:
        file_name  = f.split('.')[0]

        log_content = read_txt(log_path)
        if log_content == None: return

        if not(file_name + "\n" in log_content):
            file_path = join(couch_file_dir,f)
            fileToInflux(file_path, client, write_api, config)
        else:
            print(file_name + " already updated")

def get_file_to_load():
    file_to_load = []
    ht = pd.read_csv("history_table.csv")

    # # Check if the file has already been loaded on couchDB
    query = ht[(ht["influx_db"] == False) & (ht["file_name"].str.contains("KPI"))]
    file_to_load = query["file_name"].to_list()
    return file_to_load

def to_influx():
    print("**************************")
    print("******Influx Loading******")
    print("**************************")
    # Read the configuration file to obtain the log file path
    ConfigFile = "config.ini"
    config = configparser.ConfigParser()
    config.read(ConfigFile)

    url=config["INFLUXDB"]["influxurl"]

    if not connection_avaliable(url): return
    
    client = InfluxDBClient(url=url,
                            token=config["INFLUXDB"]["token"])

    if not bucket_exists(client, config):
        print("The bucket doesn't exist")
        return
    write_api = client.write_api(write_options=ASYNCHRONOUS)

    username = "LattepandaCouch"
    password = "peanut96"
    couch_url = "http://192.168.1.5:5984/students/"

    file_to_load = get_file_to_load()

    for file in file_to_load:
        print("Attempting to load " + file)
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
                


if __name__ == '__main__':
    to_influx("2021-03-17")
