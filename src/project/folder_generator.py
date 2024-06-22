import os
import toml
import numpy as np

FOLDER_LOCATION = '../../data'

MIN_FLOW = 0.013
MAX_FLOW = 0.6
FLOW_SAMPLES = 15

CONFIG_FILE_TEMPLATE = {
    'simulation': {'registers': 5_000},
    'tanks': {
        'flow_value': None,
        'vol': 50_000
    }
}

script_dir = os.path.dirname(os.path.abspath(__file__))

for i, val in enumerate(np.linspace(MIN_FLOW, MAX_FLOW, FLOW_SAMPLES)):
    dir_route = f'{script_dir}/{FOLDER_LOCATION}/case_{i:0>4}'
    try:
        os.makedirs(dir_route)
        print(f'Directorio \'{dir_route}\' creado correctamente')
    except Exception as e:
        print(f'Error al crear el directorio: {e}')

    CONFIG_FILE_TEMPLATE['tanks']['flow_value'] = float(val)
    toml.dump(CONFIG_FILE_TEMPLATE, open(f'{dir_route}/sim_config.toml', 'w'))
    print('\tFichero de configuración \'sim_config.toml\' generado correctamente')

    print()