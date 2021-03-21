import configparser
from os.path import normpath

def developement_config():
    global config
    global ConfigFile
    
    data_dir = "D://Documents//Uni//Tesi//ConditionPanda//Scripts//AutomationData"
    log_dir = "D://Documents//Uni//Tesi//ConditionPanda//CouchDB//Log//Log.txt"
    couch_dir = "D://Documents//Uni//Tesi//ConditionPanda//CouchDB//Log//Log.txt"
    
    config["DEWESOFT"]["data_dir"] = normpath(data_dir)
    config["DEWESOFT"]["setup_file"] = "AccSetup2.xml"
    config["DEWESOFT"]["record_duration"] = "10000"
    config["DEWESOFT"]["sampling_frequency"] = "20000"
    config["DEWESOFT"]["file_name"] = "LattePanda"
    config["DEWESOFT"]["sensor_name"] = "AI 1"
    
    config["INFLUXDB"]["measurement"] = "Monitoring"
    config["INFLUXDB"]["Org"] = "myorg"
    config["INFLUXDB"]["Token"] = "mytoken"
    config["INFLUXDB"]["KPIbucket"] = "KPI_db"
    config["INFLUXDB"]["InfluxURL"] = "http://localhost:8086"
    config["INFLUXDB"]["auto_load"] = "True"
    config["INFLUXDB"]["log_dir"] = normpath(log_dir)
    
    config["COUCHDB"]["couch_dir"] = normpath(couch_dir)
    config["COUCHDB"]["couch_url"] = "http://localhost:5984"

    with open(ConfigFile,'w') as f:
        config.write(f)
    f.close()


def production_config():
    global config
    global ConfigFile
    
    data_dir = "C://Users//LattePanda//Documents//ConditionPanda//Scripts//AutomationData"
    log_dir = "C://Users//LattePanda//Documents//ConditionPanda//CouchDB//Log//Log.txt"
    couch_dir = "C://Users//LattePanda//Documents//ConditionPanda//CouchDB"
    
    config["DEWESOFT"]["data_dir"] = normpath(data_dir)
    config["DEWESOFT"]["setup_file"] = "AccSetup2.xml"
    config["DEWESOFT"]["record_duration"] = "10000"
    config["DEWESOFT"]["sampling_frequency"] = "20000"
    config["DEWESOFT"]["file_name"] = "LattePanda"
    config["DEWESOFT"]["sensor_name"] = "AI 1"
    
    config["INFLUXDB"]["measurement"] = "Monitoring"
    config["INFLUXDB"]["Org"] = "myorg"
    config["INFLUXDB"]["Token"] = "mytoken"
    config["INFLUXDB"]["KPIbucket"] = "KPI_db"
    config["INFLUXDB"]["InfluxURL"] = "http://192.168.1.5:8086"
    config["INFLUXDB"]["auto_load"] = "True"
    config["INFLUXDB"]["log_dir"] = normpath(log_dir)
    
    config["COUCHDB"]["couch_dir"] = normpath(couch_dir)
    config["COUCHDB"]["couch_url"] = "http://192.168.1.5:5984"

    with open(ConfigFile,'w') as f:
        config.write(f)
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
    # Read config file
    ConfigFile = "config.ini"
    config = configparser.ConfigParser()
    
    config.add_section("DEWESOFT")
    config.add_section("INFLUXDB")
    config.add_section("COUCHDB")
    
    print("Avaliable configurations:")
    print("'d'   Developement")
    print("'p'   Production")
    conf = input("Enter the configuration: ")
    generate_config(conf)
