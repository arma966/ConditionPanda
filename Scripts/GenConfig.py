from json import dump 

def developementConfig():
    influxDict = {"Org": "myorg",
                  "Token": "mytoken",
                  "Measurement": "Monitoring",
                  "Client URL": "http://localhost:8086",
                  "KPI Bucket": "KPI_db",
                  "AutoLoad": "True",
                  "LogDir": "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\CouchDB\\Log\\Log.txt"
        }
    
    deweDict = {"DataDir": "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\Scripts\\AutomationData",
                "SetupFile": "AccSetup2.xml",
                "FileName": "LattePanda",
                "Record duration": 10000,
                "Sampling frequency": 20000,
                "Sensor name": "AI 1"
        }
    
    couchDict = {"couchDir": "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\CouchDB"
        }
    
    config = {"Dewesoft": deweDict,
              "InfluxDB": influxDict,
              "CouchDB": couchDict
        }

    with open('Config.json', 'w') as f:
        dump(config, f, indent = 4)
    f.close()


def productionConfig():
    influxDict = {"Org": "myorg",
                  "Token": "mytoken",
                  "Measurement": "Monitoring",
                  "Client URL": "http://localhost:8086",
                  "KPI Bucket": "KPI_db",
                  "AutoLoad": "True",
                  "LogDir": "C:\\Users\\LattePanda\\Documents\\CouchDB\\Log\\Log.txt"
        }
    
    deweDict = {"DataDir": "C:\\Users\\LattePanda\\Documents\\Scripts\\AutomationData",
                "SetupFile": "AccSetup2.xml",
                "FileName": "LattePanda",
                "Record duration": 10000,
                "Sampling frequency": 20000,
                "Sensor name": "AI 1"
        }
    
    couchDict = {"couchDir": "C:\\Users\\LattePanda\\ConditionPanda\\CouchDB"
        }
    
    config = {"Dewesoft": deweDict,
              "InfluxDB": influxDict,
              "CouchDB": couchDict
        }
    with open('Config.json', 'w') as f:
        dump(config, f, indent = 4)
    f.close()


def generateConfig(conf):
    if conf == 'd':
        developementConfig()
        print('Developement configuration correctly generated')
    elif conf == 'p':
        productionConfig()
        print('Production configuration correctly generated')
    else:
        print("Invalid parameter")

if __name__ == '__main__':
    print("Avaliable configurations:")
    print("'d'   Developement")
    print("'p'   Production")
    conf = input("Enter the configuration: ")
    generateConfig(conf)
