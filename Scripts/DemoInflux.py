from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS


import socket

def doThis():
    url = "http://localhost:8086"
    org = "myorg"
    token = "mytoken"
    
    client = InfluxDBClient(url=url, token=token)
    write_api = client.write_api(write_options=ASYNCHRONOUS)
    buckets = client.buckets_api().find_buckets().to_dict()
    data = {"measurement": "prova",
            "tags": {"location": "un posto",
                      "tag2": "un altro tag"
                },
            "fields": {"campo": 2
                },
            "time": 1
            }
    
    print("Databases:")
    print(client.get_list_database())
    
    try:
        response = write_api.write(bucket="KPI_db", record=data, org=org)
    except:
        print("Connection error: ")
    else:
        print(response.get())
        client.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('192.168.1.5',8086))
if result == 0:
    print("Port is open")
    doThis()
else:
    print("Port is not open")
sock.close()

import requests
# params = {"org": "myorg",
#           "token": "mytoken"
#     }
# url = "http://localhost:8086/api/v2/buckets/mytoken"
# response = requests.get(url,params)
# print(response.content)

# params = {"Token": "mytoken",
#           "username": "myusername",
#           "password": "peanut96"
#           }

# url = "http://localhost:8086/api/v2/signin"
# response = requests.post(url,params)
# print(response.content)
