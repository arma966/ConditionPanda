import requests
import configparser
from os.path import normpath 
import sys
# url = "http://localhost:5984/"

# try:
#     r = requests.get(url)
# except:
#     print("connection error")
# else:
#     content = r.json()
#     print(r.content.decode())
    

config = configparser.ConfigParser()


resp = config.read("config.ini")
if resp == []:
    print("The file doesn't exists")
    sys.exit()

login = config['INFLUXDB']
print(login["KPIbucket"])

config['INFLUXDB']