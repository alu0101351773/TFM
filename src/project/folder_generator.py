import os
import sys
import toml
import numpy as np

FOLDER_LOCATION = '../../data'

MIN_FLOW = 0.013
MAX_FLOW = 0.6
FLOW_SAMPLES = 15

CONFIG_FILE_TEMPLATE = {
    'simulation': {'registers': 100},
    'tanks': {
        'flow_value': None,
        'vol': 50_000
    }
}

# TODO: Hacer que el fichero pueda ser ejecutado desde cualquier ruta
script_dir = os.path.dirname(os.path.abspath(__file__))

for i, val in enumerate(np.linspace(MIN_FLOW, MAX_FLOW, FLOW_SAMPLES)):
    dir_route = f'{FOLDER_LOCATION}/case_{i:0>4}'
    try:
        os.makedirs(dir_route)
        print(f'Directorio \'{dir_route}\' creado correctamente')
    except Exception as e:
        print(f'Error al crear el directorio: {e}')

    # TODO: Incluir que el script guarde en cada directorio su fichero de configuración