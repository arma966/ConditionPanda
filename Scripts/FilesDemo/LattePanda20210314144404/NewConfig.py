from json import dump 

influxDict = {"Org": "myorg",
              "Token": "mytoken",
              "Measurement": "Monitoring",
              "Client URL": "http://localhost:8086",
              "KPI Bucket": "KPI_db"
    }

deweDict = {"DataDir": "D:\\Documents\\Uni\\Tesi\\ConditionPanda\\Scripts\\AutomationData",
            "SetupFile": "AccSetup2.xml",
            "FileName": "LattePanda",
            "Record duration": 10000,
            "Sampling frequency": 20000,
            "Sensor name": "AI 1"
    }

config = {"Dewesoft": deweDict,
          "InfluxDB": influxDict
    }

with open('NewConfig.json', 'w') as f:
    dump(config, f, indent = 4)
f.close()
del deweDict
del influxDict
