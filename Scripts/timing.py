import timeit
function ='''
import re
import matplotlib.pyplot as plt 
# import json
# def write_json(data, name):
#     # Write the json file
#     with open(name, 'w') as f:
#         json.dump(data, f)
#     f.close()
    
# def load_json(name):
#     with open(name,'r') as f:
#         FFT_data = f.readline()
#     f.close()
#     jdata = json.loads(FFT_data)
#     return jdata


def _read_file(file_name):
    try:
        with open(file_name,'r') as f:
            FFT_data = f.readlines()
        f.close()
    except FileNotFoundError:
        print("File not found")
        return
    else:
        return FFT_data


def _is_number(num):
    try:
        float(num)
    except ValueError:
        return False
    else:
        return True


def _find_start_index(FFT_data):
    for i, line in enumerate(FFT_data):
        if _is_number(line[0:5]):
            return i-1


def parse_data(FFT_data):
    start_index = _find_start_index(FFT_data)    
    
    header = FFT_data[start_index]
    header = header.replace('Time (s),'," ")
    header = re.sub('AI 1/AmplFFT \(',"", header)
    header = re.sub('(?<=\d) Hz\)',",", header)
    del FFT_data[0:start_index]
    
    FFT_data[0] = header
    
    for i,value in enumerate(FFT_data):
        value = list(value.split(","))[0:-1]
        value = [float(ele) for ele in value]
        FFT_data[i] = value
    return FFT_data


file_name = "file3.txt"
FFT_data_parsed = parse_data(_read_file(file_name))
'''
print (timeit.timeit(stmt = function,
                     number = 100)/100)

