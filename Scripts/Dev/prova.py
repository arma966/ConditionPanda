import pandas as pd

def get_file_to_load():
    file_to_load = []
    ht = pd.read_csv("history_table.csv")
    
    # # Check if the file has already been loaded on couchDB
    query = ht[(ht["influx_db"] == False) & (ht["file_name"].str.contains("KPI"))]
    file_to_load = query["file_name"].to_list()
    return file_to_load

file_to_load = get_file_to_load()
