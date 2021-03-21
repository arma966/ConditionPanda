"""
____________________________________________________________________________
Utilities to create a dictionary based data structure from the Dewesoft-exported
files. The data structure is then coverted to the json format. 

Author: Armenante Davide
Last update: 20/3/2021
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

def get_metadata(file_path):
    # Read the firsts few lines of the *FileName* and retrieve the metadata 
    # creating a dictionary.
    metaDictionary =  {}
    read = True
    with open(file_path) as f:
        while read:
            tmp = f.readline()
            if not(tmp == "\n"):
                if not(tmp.find(":") == -1):
                    s = tmp.strip().split(": ",maxsplit = 1)
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
                    i = i+1
    except FileNotFoundError:
        print("Can't retrieve the data, the file doesn't exist.")
        return None
    else:
        f.close()
        
        # Load data as numpy array
        data= loadtxt(file_path, delimiter=",",skiprows=rowsToSkip)
        return data

def build_KPI_dictionary(file_dir):
    # Read all the exported file and create a data structure based on nested
    # dictionaries. 
    
    # Get the file list
    file_list = [f for f in listdir(file_dir) if isfile(join(file_dir, f)) 
                        and not(f.find('_') == -1)]
    
    # IMPORTANT: for the future updates it is mandatory to iterate through 
    # the sensor's names
    sensor_name = "AI 1"
    # Build KPI dictionary
    KPI_dict = {"Time": {},
               "Frequency": {}}
    
    for f in file_list:
        file_path = join(file_dir,f)
        data = get_data(file_path)
        if data is not(None):
            KPI_names = f[f.find("_")+1:f.find(".")].replace(" ","_")
            time_dictionary = {"Dt": round((data[1,0]-data[0,0])*1000,2),
                               "data": data[:,1].tolist()}
            KPI_dict["Time"][KPI_names] = time_dictionary
        
        
    
    # Build sensor dictionary
    # Get the sensor data from the csv table
    try:
        sensor_table = read_csv("SensorTable.csv")
        sensor_spec = sensor_table.query("Dewe_name == "+ '"'+sensor_name+'"')
    except KeyError:
        print("Sensor not present in the table")
        sensor_dictionary = {}
        sensor_dictionary["KPI"] = KPI_dict
        return None
    except FileNotFoundError:
        print("Make sure the sensor table file and the python script are in the same directory")
        sensor_dictionary = {}
        sensor_dictionary["KPI"] = KPI_dict
        return None
    else:
        sensor_dictionary = {sensor_name: {
                      "MOD": sensor_spec["MOD"].to_string(index = False).replace(' ',''),
                      "MAC": sensor_spec["MAC"].to_string(index = False).replace(' ',''),
                      "LOC": sensor_spec["LOC"].to_string(index = False).replace(' ',''),
                      "KPI": KPI_dict
                      }
            }
    
    raw_file_path = join(file_dir,file_list[0])
    metaDataFile = get_metadata(raw_file_path)
    
    # Build main dictionary
    # Build main dictionary
    retrieved_date = datetime.strptime(metaDataFile["Start time"], '%m/%d/%Y %H:%M:%S.%f')
    delta = timedelta(milliseconds=int(metaDataFile["Post time"]))
    end_time = retrieved_date + delta
    
    json_id = "KPI-" + get_shot(retrieved_date.isoformat())
    KPI_dict = {
                "_id": json_id,
                "DV": sensor_spec["DV"].to_string(index = False).replace(' ',''),
                "DAQ": sensor_spec["DAQ"].to_string(index = False).replace(' ',''),
                "MU": "m/s2",
                "S": sensor_dictionary,
                "AST": retrieved_date.isoformat(),
                "AET": end_time.isoformat(),
                "SF": metaDataFile["Sample rate"],
                "PT": metaDataFile["Post time"],
        }
    return KPI_dict

def build_RAW_dictionary(file_dir):
    # Build the dictionary based data structure, see build_KPI_dictionary().
    
    # IMPORTANT: for the future updates it is mandatory to iterate through 
    # the sensor's names
    sensor_name = "AI 1"
    
    # Get the file list
    file_list = [f for f in listdir(file_dir) if isfile(join(file_dir, f)) 
                        and f.find('_') == -1 and not(f.find('.txt') == -1) ]
    
    try:
        file_path = join(file_dir,file_list[0])
        data = get_data(file_path)
    except:
        print("Impossible to retrieve raw data")
    
    
    # Build sensor dictionary
    sensor_table = read_csv("SensorTable.csv")
    sensor_spec = sensor_table.query("Dewe_name == "+ '"'+sensor_name+'"')
    sensor_dictionary = {sensor_name: {
                  "MOD": sensor_spec["MOD"].to_string(index = False).replace(' ',''),
                  "MAC": sensor_spec["MAC"].to_string(index = False).replace(' ',''),
                  "LOC": sensor_spec["LOC"].to_string(index = False).replace(' ',''),
                  "Data": data[:,1].tolist()
                  }
        }
    file_path = join(file_dir,file_list[0])
    metaDataFile = get_metadata(file_path)
    
    # Build main dictionary
    retrieved_date = datetime.strptime(metaDataFile["Start time"], '%m/%d/%Y %H:%M:%S.%f')
    delta = timedelta(milliseconds=int(metaDataFile["Post time"]))
    end_time = retrieved_date + delta
    
    json_id = "RAW-" + get_shot(retrieved_date.isoformat())
    KPI_dict = {
                "_id": json_id,
                "DV": sensor_spec["DV"].to_string(index = False).replace(' ',''),
                "DAQ": sensor_spec["DAQ"].to_string(index = False).replace(' ',''),
                "MU": "m/s2",
                "S": sensor_dictionary,
                "AST": retrieved_date.isoformat(),
                "AET": end_time.isoformat(),
                "SF": int(metaDataFile["Sample rate"]),
                "PT": int(metaDataFile["Post time"]),
        }
    return KPI_dict

def get_shot(date):
    try:
        datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        print("[get_shot()] Wrong date format on the exported Dewesoft file.")
        print("Make sure the system date format follows the ISO standard 8601")
        return None
    else:
        shot = date.replace("-","").replace("T","").replace(":","")
        shot = shot.replace(".","")[0:-3]
        return shot

def write_json(data, name):
    # Write the json file
    with open(name, 'w') as f:
        dump(data, f)
    f.close()

def get_target_path(couch_dir, date):
    dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
    target_path = join(couch_dir,str(dt.year),str(dt.month),str(dt.day))
    if not(exists(target_path)):
        if not(exists(join(couch_dir,str(dt.year),str(dt.month)))):
            if not(exists(join(couch_dir,str(dt.year)))):
                mkdir(join(couch_dir,str(dt.year)))
                mkdir(join(couch_dir,str(dt.year),str(dt.month)))
                mkdir(join(couch_dir,str(dt.year),str(dt.month),str(dt.day)))
            else:
                mkdir(join(couch_dir,str(dt.year),str(dt.month)))
                mkdir(join(couch_dir,str(dt.year),str(dt.month),str(dt.day)))
        else:
            mkdir(join(couch_dir,str(dt.year),str(dt.month),str(dt.day)))
    return target_path

def to_couchDB():
    ConfigFile = "config.ini"
    config = configparser.ConfigParser()
    config.read(ConfigFile)
    
    data_dir = config["DEWESOFT"]["data_dir"]
    couch_dir = config["COUCHDB"]["couch_dir"]
    dewe_folder_list = [f for f in listdir(data_dir) if isdir(join(data_dir, f))]
    
    if dewe_folder_list == []:
        print("There are no data acquired by the DAQ")
        return
    
    # For every folder created by exporting the acquired files, navigate through
    # it and upload the data to couchDB
    for f in dewe_folder_list:
        dewe_data_path = join(data_dir,f)
        
        KPI_dict = build_KPI_dictionary(dewe_data_path)
        RAW_dict = build_RAW_dictionary(dewe_data_path)
        
        if KPI_dict is not(None) and RAW_dict is not(None):
            shot = get_shot(KPI_dict["AST"])
            if shot is not(None):
                target_path = get_target_path(couch_dir, KPI_dict["AST"])
                
                KPI_dictName = shot + "KPI.json"
                RAW_dictName = shot + "Raw.json"
                print("Uploading shot: " + shot + " to CouchDB")
                write_json(KPI_dict, join(target_path,KPI_dictName))
                write_json(RAW_dict, join(target_path,RAW_dictName))
                
                # Remove dewesoft files
                rmtree(dewe_data_path)
                remove(dewe_data_path + '.dxd')

if __name__ == '__main__':
    to_couchDB()