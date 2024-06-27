import os
import subprocess
from tqdm import tqdm

DATASET_NUMBER = 2

DATA_FOLDER = '../../data'
script_dir = os.path.dirname(os.path.abspath(__file__))
dir_route = f'{script_dir}/{DATA_FOLDER}'

for folder in tqdm(os.listdir(dir_route)):
    if len(os.listdir(f'{dir_route}/{folder}')) != 1:
        # print(f'Data in {folder} has already been generated!')
        continue
    for i in range(DATASET_NUMBER):
        subprocess.run(
            ['python', f'{script_dir}/../simulator/sim_plant.py', f'{dir_route}/{folder}'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )