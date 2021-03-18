from json import dump 

def developement_config():
    influx_dict = {"Org": "myorg",
                  "Token": "mytoken",
                  "Measurement": "Monitoring",
                  "Client URL": "http://localhost:8086",
                  "KPI Bucket": "KPI_db",
                  "AutoLoad": "True",
                  "LogDir": "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\CouchDB\\Log\\Log.txt"
        }
    
    dewe_dict = {"DataDir": "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\Scripts\\AutomationData",
                "SetupFile": "AccSetup2.xml",
                "FileName": "LattePanda",
                "Record duration": 10000,
                "Sampling frequency": 20000,
                "Sensor name": "AI 1"
        }
    
    couch_dict = {"couchDir": "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\CouchDB"
        }
    
    config = {"Dewesoft": dewe_dict,
              "InfluxDB": influx_dict,
              "CouchDB": couch_dict
        }

    with open('Config.json', 'w') as f:
        dump(config, f, indent = 4)
    f.close()


def production_config():
    influx_dict = {"Org": "myorg",
                  "Token": "mytoken",
                  "Measurement": "Monitoring",
                  "Client URL": "http://192.168.1.5:8086",
                  "KPI Bucket": "KPI_db",
                  "AutoLoad": "True",
                  "LogDir": "C:\\Users\\LattePanda\\Documents\\ConditionPanda\\CouchDB\\Log\\Log.txt"
        }
    
    dewe_dict = {"DataDir": "C:\\Users\\LattePanda\\Documents\\ConditionPanda\\Scripts\\AutomationData",
                "SetupFile": "AccSetup2.xml",
                "FileName": "LattePanda",
                "Record duration": 10000,
                "Sampling frequency": 20000,
                "Sensor name": "AI 1"
        }
    
    couch_dict = {"couchDir": "C:\\Users\\LattePanda\\Documents\\ConditionPanda\\CouchDB"
        }
    
    config = {"Dewesoft": dewe_dict,
              "InfluxDB": influx_dict,
              "CouchDB": couch_dict
        }
    with open('Config.json', 'w') as f:
        dump(config, f, indent = 4)
    f.close()


def generate_config(conf):
    if conf == 'd':
        developement_config()
        print('Developement configuration correctly generated')
    elif conf == 'p':
        production_config()
        print('Production configuration correctly generated')
    else:
        print("Invalid parameter")

if __name__ == '__main__':
    print("Avaliable configurations:")
    print("'d'   Developement")
    print("'p'   Production")
    conf = input("Enter the configuration: ")
    generate_config(conf)
