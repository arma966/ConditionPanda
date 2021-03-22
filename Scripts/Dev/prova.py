import requests
from requests.auth import HTTPBasicAuth

username = "LattepandaCouch"
password = "peanut96"
couch_url = "http://localhost:5984/students/"


file_list = ["KPI-20210321230701824",
             "KPI-20210321233203776"]
for file in file_list:
    resp = requests.get(couch_url + file,
                                    auth=HTTPBasicAuth(username, password))
    
    print(resp.json())
    print("")
    print("")
    print("")