"""
    Retrieve from couchDB the RAW data file and plot the signal spectrum
    
    Spectrum data are formatted as follow:
        the first row represents the frequency labels;
        the i-th row represents the amplitude values of fft (block);
        the first column represents the start time of the corresponding block
        in seconds.
"""

import configparser
import requests
from requests.auth import HTTPBasicAuth
import numpy as np
import matplotlib.pyplot as plt

config_path = "C:\\Users\\LattePanda\\Documents\\ConditionPanda\\Scripts\\congif.ini"


def get_file(file_name):
    config_file = "config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    username = config["COUCHDB"]["username"]
    password = config["COUCHDB"]["password"]
    couch_url = config["COUCHDB"]["couch_url"]
    couch_db = config["COUCHDB"]["database"]

    file_url = couch_url + "/" + couch_db + "/" + file_name
    try:
        resp = requests.get(file_url, auth=HTTPBasicAuth(username, password))

    except Exception as e:
        print("Ex: " + str(e))
        return None
    else:
        return resp.json()



file_name = "RAW-20210327174447832"

data_dict = get_file("RAW-20210327174447832")

#%%

# Read spectrum
fft_data = np.array(data_dict["S"]["AI 1"]["FFT"]["spectrum"])
df = 0.5
freq_lim = 2300
n_blocks = fft_data.shape[0] - 1

# Plot
fig = plt.figure(figsize=(7, 5))
fig.set_dpi(300.0)
fig.suptitle("""Frequency spectrum""", fontweight="bold")
plt.xlabel("f [Hz]")
plt.ylabel("Amplitude $[m/s^2]$")

for i in range(n_blocks):
    print(str(i))
    plt.plot(
        fft_data[0, 1: int(freq_lim / df)],
        fft_data[i + 1, 1: int(freq_lim / df)],
        linewidth=0.8,
    )
