from os.path import join
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from math import floor

def nice_plot(v):
    fig, ax = plt.subplots()
    ax.plot(v)
    
    ax.set(xlabel='None', ylabel='None',
           title='unknown signal')
    ax.grid()

def load_file():
    file_dir = "C:\\Users\\arma9\\Documents\\DatiTesi\\AutmData20201116172227142.json"
    with open(file_dir) as f:
        content = json.load(f)
    f.close()
    return content


content = load_file()

data_list = []

for i,value in enumerate(content["aTs"][0]["aM"]):
    data_list.append(value["aV"][0])
    
nice_plot(data_list)