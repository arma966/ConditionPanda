import pandas as pd

def upload_history_table(new_file_name, loaded):
    ht = pd.read_csv("history_table.csv")
    
    new_file_entry = {"file_name": new_file_name, 
                "couch_db": False, 
                "influx_db": False
        }
    
    
    # Check if the file exist in the table
    query = ht[(ht["file_name"] == new_file_name)]
    if query.empty:
        ht = ht.append(new_file_entry, ignore_index=True)
        ht.to_csv("history_table.csv", index = False)
    
    
    # Check if the file has already been loaded on couchDB
    query = ht[(ht["file_name"] == new_file_name) & (ht["couch_db"] == False)]
    if not query.empty:
        if loaded:
            row_index = query.index[0]
            ht.loc[row_index,"couch_db"] = True
            ht.to_csv("history_table.csv", index = False)
    else:
        print(new_file_name + " already uploaded to couchDB")
    
new_file_name = "KPI-111111118"
upload_history_table(new_file_name, True)
