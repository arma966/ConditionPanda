from os.path import join
import json
import matplotlib.pyplot as plt
import numpy as np
from math import floor
import os 
def plot_matrix(matrix_data):
    fig, axs = plt.subplots(6, 1)
    axs[0].plot(matrix_data[0,:])
    axs[0].grid(True)
    axs[1].plot(matrix_data[1,:])
    axs[1].grid(True)
    axs[2].plot(matrix_data[2,:])
    axs[2].grid(True)
    axs[3].plot(matrix_data[3,:])
    axs[3].grid(True)
    axs[4].plot(matrix_data[4,:])
    axs[4].grid(True)
    axs[5].plot(matrix_data[5,:])
    axs[5].grid(True)
    
    # fig.tight_layout()
    
def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result[result.size/2:]

def rms(data_array):
    f = 10000
    dur = 60*3+59.999
    n_lines = len(data_array)
    
    
    block_size = 0.5
    lines_per_block = block_size*f
    n_blocks = floor(dur/block_size)
    time = np.linspace(0,dur,n_lines)
    
    rms_vector = np.zeros(n_blocks)
    for i in range(n_blocks):
        start_index =int(lines_per_block*i)
        stop_index = int(lines_per_block*(i+1))
        a2 = np.power(data_array[start_index:stop_index],2)
        rms_vector[i]=np.sqrt(np.sum(a2))
    return rms_vector

def nice_plot(v):
    fig, ax = plt.subplots()
    ax.plot(v)
    
    ax.set(xlabel='None', ylabel='V',
           title='Raw vibration data')
    ax.grid()

def load_file(file_path):
    with open(file_path) as f:
        content = json.load(f)
    f.close()
    return content
file_dir = "C:\\Users\\arma9\\Documents\\DatiTesi\\1\\json"
file_list = os.listdir(file_dir)

data_list = []
for file in file_list:
    data_dict = load_file(join(file_dir,file))
    data_list.append(data_dict)
del file_list
del file_dir
del file
del data_dict

# data_array = np.array(content["aV"])

#%%
matrix_data = np.zeros((6,2400000))
matrix_rms = np.zeros((6,239*2+1))
matrix_autocorr = np.zeros((6,1200000))
for i,ele in enumerate(data_list):
    matrix_data[i,:] = np.array(data_list[i]["aV"])
    matrix_rms[i,:] = rms(matrix_data[i,:])
    matrix_autocorr[i,:] = autocorr(matrix_data[i,:])



#%%
plot_matrix(matrix_rms)

