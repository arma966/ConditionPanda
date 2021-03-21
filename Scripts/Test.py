import configparser
from datetime import datetime

# def test_configFile():
#     production_key_list = ['org','token','measurement','influxurl','kpibucket', \
#                            'autoload','logdir','datadir','setupfile','filename', \
#                            'recordduration','samplingfrequency','sensorname', \
#                            'couchdir', 'couchurl']
#     key_list= []
#     for section in config:
#         for key in config[section]:
#             key_list.append(key)

    
#     # Check if key_list is a subset of production_key_list
#     common_elements = [ele for ele in key_list \
#                        if (ele in production_key_list)]
    
#     missing_keys = []
#     for key in production_key_list:
#         if key not in common_elements:
#             missing_keys.append(key) 
#     return missing_keys
            
# # Read config file
# global config
# ConfigFile = "config.ini"
# config = configparser.ConfigParser()
# config.read(ConfigFile)
# # if config.read(ConfigFile) == []: 
# #     print("Can't find the config file")
# #     sys.exit()
# missing = test_configFile()
a="2021-03-12T12:30:31.456000"
datetime.strptime(a, '%Y-%m-%dT%H:%M:%S.%f')
