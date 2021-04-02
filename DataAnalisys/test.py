from os.path import join
import json
import matplotlib.pyplot as plt
import numpy as np
from math import floor
def nice_plot(v):
    fig, ax = plt.subplots()
    ax.plot(v)
    
    ax.set(xlabel='None', ylabel='V',
           title='Raw vibration data')
    ax.grid()
    
file_name = "ChID1_2021213101814636_Alg.json"
data_dir = "C:\\Users\\arma9\\Documents\\DatiTesi"

file_path = join(data_dir,file_name)

with open(file_path) as f:
    content = json.load(f)
f.close()

data_array = np.array(content["aV"])
#%%
def rms(data_array):
    f = 10000
    dur = 60*3+59.999
    n_lines = len(data_array)
    
    
    block_size = 1
    lines_per_block = block_size*f
    n_blocks = floor(dur/block_size)
    time = np.linspace(0,dur,n_lines)
    
    rms_vector = np.zeros(n_blocks)
    for i in range(n_blocks):
        start_index =lines_per_block*i
        stop_index = lines_per_block*(i+1)
        a2 = np.power(data_array[start_index:stop_index],2)
        rms_vector[i]=np.sqrt(np.sum(a2))
    return rms_vector()

nice_plot(rms_vector)


