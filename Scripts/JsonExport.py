"""
____________________________________________________________________________
Utilities to create a dictionary based data structure from the Dewesoft-exported
files. The data structure is then coverted to the json format. 

Author: Armenante Davide
Last update: 26/3/2021
____________________________________________________________________________
"""

from numpy import loadtxt
from os import listdir, mkdir, remove
from os.path import join, isfile, isdir, exists
from datetime import datetime, timedelta
from pandas import read_csv
from shutil import rmtree
import configparser
from json import dump
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import re
from urllib.request import urlopen


def connection_avaliable(host, host_name):
    try:
        urlopen(host, timeout=2)
        return True
    except Exception as e:
        print(host_name + " connection not avaliable")
        print(str(e))
        return False


def read_file(file_name):
    try:
        with open(file_name, "r") as f:
            fft_data = f.readlines()
        f.close()
    except FileNotFoundError:
        print("File not found")
        return None
    else:
        return fft_data


def is_number(num):
    try:
        float(num)
    except ValueError:
        return False
    else:
        return True


def find_start_index(fft_data):
    for i, line in enumerate(fft_data):
        if is_number(line[0:5]):
            return i - 1
    print("Start index not found")
    return None


def parse_data(file_name):
    fft_data = read_file(file_name)
    start_index = find_start_index(fft_data)

    header = fft_data[start_index]
    header = header.replace("Time (s),", " ")
    header = re.sub("AI 1/AmplFFT \(", "", header)
    header = re.sub("(?<=\d) Hz\)", ",", header)
    del fft_data[0:start_index]

    fft_data[0] = header

    for i, value in enumerate(fft_data):
        value = list(value.split(","))[0:-1]
        value = [float(ele) for ele in value]
        fft_data[i] = value
    return fft_data


def get_metadata(file_path):
    # Read the firsts few lines of the *FileName* and retrieve the metadata
    # creating a dictionary.
    metaDictionary = {}
    read = True
    with open(file_path) as f:
        while read:
            tmp = f.readline()
            if not (tmp == "\n"):
                if not (tmp.find(":") == -1):
                    s = tmp.strip().split(": ", maxsplit=1)
                    metaDictionary[s[0]] = s[1]
            else:
                read = False
    f.close()
    return metaDictionary


def get_data(file_path):
    # Skip the rows which contain the metadata and get the data from *FileName*
    # as a numpy array.

    # Get the number of rows to skip
    read = True
    try:
        with open(file_path) as f:
            i = 0
            while read:
                tmp = f.readline()
                if tmp[0].isnumeric():
                    read = False
                    rowsToSkip = i
                else:
                    i = i + 1
    except FileNotFoundError:
        print("Can't retrieve the data, the file doesn't exist.")
        return None
    else:
        f.close()

        # Load data as numpy array
        data = loadtxt(file_path, delimiter=",", skiprows=rowsToSkip)
        return data


def build_KPI_dictionary(file_dir):
    # Read all the exported file and create a data structure based on nested
    # dictionaries.

    # Get the file list
    time_file_list = [
        f
        for f in listdir(file_dir)
        if isfile(join(file_dir, f)) 
        and not (f.find("_") == -1) 
        and f.find("FFT") == -1
    ]

    # IMPORTANT: for the future updates it is mandatory to iterate through
    # the sensor's names
    sensor_name = "AI 1"
    # Build KPI dictionary
    KPI_dict = {"Time": {}, "Frequency": {}}

    for f in time_file_list:
        file_path = join(file_dir, f)
        data = get_data(file_path)
        if data is not (None):
            KPI_names = f[f.find("_") + 1 : f.find(".")].replace(" ", "_")
            time_dictionary = {
                "Dt": round((data[1, 0] - data[0, 0]) * 1000, 2),
                "data": data[:, 1].tolist(),
            }
            KPI_dict["Time"][KPI_names] = time_dictionary

    # Build sensor dictionary
    # Get the sensor data from the csv table
    try:
        sensor_table = read_csv("SensorTable.csv")
        sensor_spec = sensor_table.query("Dewe_name == " 
                                         + '"' 
                                         + sensor_name 
                                         + '"')
    except KeyError:
        print("Sensor not present in the table")
        sensor_dictionary = {}
        sensor_dictionary["KPI"] = KPI_dict
        return None
    except FileNotFoundError:
        print(
            "Make sure the sensor table file and the python script are in the same directory"
        )
        sensor_dictionary = {}
        sensor_dictionary["KPI"] = KPI_dict
        return None
    else:
        sensor_dictionary = {
            sensor_name: {
                "MOD": sensor_spec["MOD"].to_string(index=False).replace(" ", ""),
                "MAC": sensor_spec["MAC"].to_string(index=False).replace(" ", ""),
                "LOC": sensor_spec["LOC"].to_string(index=False).replace(" ", ""),
                "KPI": KPI_dict,
            }
        }

    raw_file_path = join(file_dir, time_file_list[0])
    meta_data = get_metadata(raw_file_path)

    # Build main dictionary
    # Build main dictionary
    retrieved_date = datetime.strptime(meta_data["Start time"], 
                                       "%m/%d/%Y %H:%M:%S.%f")
    delta = timedelta(milliseconds=int(meta_data["Post time"]))
    end_time = retrieved_date + delta

    json_id = "KPI-" + get_shot(retrieved_date.isoformat())
    KPI_dict = {
        "_id": json_id,
        "DV": sensor_spec["DV"].to_string(index=False).replace(" ", ""),
        "DAQ": sensor_spec["DAQ"].to_string(index=False).replace(" ", ""),
        "MU": "m/s2",
        "S": sensor_dictionary,
        "AST": retrieved_date.isoformat(),
        "AET": end_time.isoformat(),
        "SF": meta_data["Sample rate"],
        "PT": meta_data["Post time"],
        "Type": "KPI"
    }
    return KPI_dict


def build_RAW_dictionary(file_dir):
    # Build the dictionary based data structure, see build_KPI_dictionary().

    # IMPORTANT: for the future updates it is mandatory to iterate through
    # the sensor's names
    sensor_name = "AI 1"

    # Get the file list
    time_file_list = [
        f
        for f in listdir(file_dir)
        if isfile(join(file_dir, f))
        and f.find("_") == -1
        and not (f.find(".txt") == -1)
    ]

    fft_file_list = [
        f
        for f in listdir(file_dir)
        if isfile(join(file_dir, f))
        and not (f.find("FFT") == -1)
        and (f.find("block") == -1)
    ]

    file_path = join(file_dir, time_file_list[0])
    fft_file_path = join(file_dir, fft_file_list[0])

    try:
        data = get_data(file_path)
    except:
        print("Impossible to retrieve raw data")
        return

    meta_data = get_metadata(file_path)

    # Build main dictionary
    retrieved_date = datetime.strptime(meta_data["Start time"], 
                                       "%m/%d/%Y %H:%M:%S.%f")
    delta = timedelta(milliseconds=int(meta_data["Post time"]))
    end_time = retrieved_date + delta

    json_id = "RAW-" + get_shot(retrieved_date.isoformat())

    # Build FFT dictionary
    fft_dict = {"Df": 0.5, 
                "Window": "Blackman", 
                "spectrum": parse_data(fft_file_path)}
    # Build sensor dictionary
    sensor_table = read_csv("SensorTable.csv")
    sensor_spec = sensor_table.query("Dewe_name == " + '"' + sensor_name + '"')
    sensor_dictionary = {
        sensor_name: {
            "MOD": sensor_spec["MOD"].to_string(index=False).replace(" ", ""),
            "MAC": sensor_spec["MAC"].to_string(index=False).replace(" ", ""),
            "LOC": sensor_spec["LOC"].to_string(index=False).replace(" ", ""),
            "TimeData": data[:, 1].tolist(),
            "FFT": fft_dict,
        }
    }

    RAW_dict = {
        "_id": json_id,
        "DV": sensor_spec["DV"].to_string(index=False).replace(" ", ""),
        "DAQ": sensor_spec["DAQ"].to_string(index=False).replace(" ", ""),
        "MU": "m/s2",
        "S": sensor_dictionary,
        "AST": retrieved_date.isoformat(),
        "AET": end_time.isoformat(),
        "SF": int(meta_data["Sample rate"]),
        "PT": int(meta_data["Post time"]),
        "Type": "RAW"
    }
    return RAW_dict


def get_shot(date):
    try:
        datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        print("[get_shot()] Wrong date format on the exported Dewesoft file.")
        print("Make sure the system date format follows the ISO standard 8601")
        return None
    else:
        shot = date.replace("-", "").replace("T", "").replace(":", "")
        shot = shot.replace(".", "")[0:-3]
        return shot


def write_json(data, name):
    # Write the json file
    with open(name, "w") as f:
        dump(data, f)
    f.close()


def get_target_path(couch_dir, date):
    dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
    target_path = join(couch_dir, str(dt.year), str(dt.month), str(dt.day))
    if not (exists(target_path)):
        if not (exists(join(couch_dir, str(dt.year), str(dt.month)))):
            if not (exists(join(couch_dir, str(dt.year)))):
                mkdir(join(couch_dir, str(dt.year)))
                mkdir(join(couch_dir, str(dt.year), str(dt.month)))
                mkdir(join(couch_dir, str(dt.year), str(dt.month), str(dt.day)))
            else:
                mkdir(join(couch_dir, str(dt.year), str(dt.month)))
                mkdir(join(couch_dir, str(dt.year), str(dt.month), str(dt.day)))
        else:
            mkdir(join(couch_dir, str(dt.year), str(dt.month), str(dt.day)))
    return target_path


def update_history_table(new_file_name, loaded):
    ht = pd.read_csv("history_table.csv")

    new_file_entry = {"file_name": new_file_name, 
                      "couch_db": False, 
                      "influx_db": False}

    # Check if the file exist in the table
    query = ht[(ht["file_name"] == new_file_name)]
    if query.empty:
        ht = ht.append(new_file_entry, ignore_index=True)
        ht.to_csv("history_table.csv", index=False)

    # Check if the file has already been loaded on couchDB
    query = ht[(ht["file_name"] == new_file_name) & (ht["couch_db"] == False)]
    if not query.empty:
        if loaded:
            row_index = query.index[0]
            ht.loc[row_index, "couch_db"] = True
            ht.to_csv("history_table.csv", index=False)
    else:
        print(new_file_name + " already uploaded to couchDB")


def load_kpi(KPI_dict, config, KPI_file_name):
    username = config["COUCHDB"]["username"]
    password = config["COUCHDB"]["password"]
    couch_url = config["COUCHDB"]["couch_url"]
    shot = get_shot(KPI_dict["AST"])
    couch_db = config["COUCHDB"]["database"]
    KPI_file_name = "KPI-" + shot
    try:
        resp = requests.put(
            couch_url + "/" + couch_db + "/" + KPI_file_name,
            auth=HTTPBasicAuth(username, password),
            json=KPI_dict,
        )

    except:
        print("Can't load the file on CouchDB, an exception occurred")
        return False
    else:
        if resp.status_code == 409:
            print("File already in CouchDB")
            return True
        elif resp.status_code == 201:
            print("CouchDB KPI loading successful: " + str(resp.status_code))
            return True
        else:
            print(resp.text)
            print("Error, can't load the file on CouchDB: " 
                  + str(resp.status_code))
            return False


def load_raw(RAW_dict, config, RAW_file_name):
    username = config["COUCHDB"]["username"]
    password = config["COUCHDB"]["password"]
    couch_url = config["COUCHDB"]["couch_url"]
    couch_db = config["COUCHDB"]["database"]
    shot = get_shot(RAW_dict["AST"])
    
    RAW_file_name = "RAW-" + shot
    try:
        resp = requests.put(
            couch_url + "/" + couch_db + "/" + RAW_file_name,
            auth=HTTPBasicAuth(username, password),
            json=RAW_dict,
        )

    except:
        print("Can't load the file on CouchDB, an exception occurred")
        return False
    else:
        if resp.status_code == 409:
            print("File already in CouchDB")
            return True
        elif resp.status_code == 201:
            print("CouchDB RAW loading successful: " + str(resp.status_code))
            return True
        else:
            print(resp.text)
            print("Error, can't load the file on CouchDB: " 
                  + str(resp.status_code))
            return False


def to_couchDB():
    print("\n------CouchDB Upload------")
    ConfigFile = "config.ini"
    config = configparser.ConfigParser()
    config.read(ConfigFile)
    
    couch_url = config["COUCHDB"]["couch_url"]
    data_dir = config["DEWESOFT"]["data_dir"]

    dewe_folder_list = [f for f in listdir(data_dir) 
                        if isdir(join(data_dir, f))]

    if dewe_folder_list == []:
        print("There are no data acquired by the DAQ")
        return

    """
    | For every folder created by exporting the acquired files, navigate 
    | through it and upload the data to couchDB
    """
    for f in dewe_folder_list:
        if not connection_avaliable(host=couch_url, host_name="CouchDB"):
            return
        dewe_data_path = join(data_dir, f)

        KPI_dict = build_KPI_dictionary(dewe_data_path)
        RAW_dict = build_RAW_dictionary(dewe_data_path)

        loaded_KPI = False
        loaded_RAW = False

        shot = get_shot(KPI_dict["AST"])
        if shot is None:
            return

        KPI_file_name = "KPI-" + shot
        RAW_file_name = "RAW-" + shot

        if KPI_dict is not (None) and RAW_dict is not (None):
            result = load_kpi(KPI_dict, config, KPI_file_name)
            if result:
                loaded_KPI = True
            result = load_raw(RAW_dict, config, RAW_file_name)
            if result:
                loaded_RAW = True

        update_history_table(RAW_file_name, loaded_RAW)
        update_history_table(KPI_file_name, loaded_KPI)

        if loaded_KPI and loaded_RAW:
            # Remove dewesoft files
            try:
                rmtree(dewe_data_path)
                remove(dewe_data_path + ".dxd")
            except FileNotFoundError:
                print(dewe_data_path + ".dxd" + " already removed")


if __name__ == "__main__":
    to_couchDB()
