import os
import toml
import numpy as np
import subprocess

DATASET_NUMBER = 3

DATA_FOLDER = '../../data'
script_dir = os.path.dirname(os.path.abspath(__file__))
dir_route = f'{script_dir}/{DATA_FOLDER}'

for folder in os.listdir(dir_route):
    for i in range(DATASET_NUMBER):
        subprocess.run(['python', f'{script_dir}/../simulator/sim_plant.py', f'{dir_route}/{folder}'])