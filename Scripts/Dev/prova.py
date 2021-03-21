import requests
from requests.auth import HTTPBasicAuth
import json

username = "LattepandaCouch"
password = "peanut96"
file_id = "KPI-20210321154238651"
url = "http://localhost:5984/students/" + file_id

with open('file.json','r') as f:
    data = json.load(f)
f.close()

try:
    resp = requests.put(url,auth=HTTPBasicAuth(username, password),json = data)
except:
    print("Can't load the file on CouchDB, an exception occurred")
else: 
    if resp.status_code != 201:
        print(resp.text)
        print("status code: " + str(resp.status_code))