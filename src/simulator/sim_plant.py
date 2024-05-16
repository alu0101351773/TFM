# -*- coding: utf-8 -*-
"""
@author: Yanes Pérez, Nicolás
@version: v1.0
---------------------------------------------------------------------------------------
SIMULACIÓN DE LA PLANTA

Por medio de la simulación y creando el control de la planta
---------------------------------------------------------------------------------------
"""

import json
import matplotlib
import os
import sys
import toml

from tank import *
from plant import *

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(script_dir, 'inventario-1anio.csv')

with open(os.path.join(script_dir, 'tanks.json')) as f:
  data_tanks = json.load(f)

with open(os.path.join(script_dir, 'inputs_user.json')) as f:
  data_inputs = json.load(f)

with open(os.path.join(script_dir, 'simulation.json')) as f:
  data_simulation = json.load(f)
  t_initial = data_simulation['log_initial']
  t_step = data_simulation['log_step']
  t_end = data_simulation['log_end']
  t_cycle = data_simulation['sim_step']


# Fragmento de fichero de configuracion adicional para no modificar
extra_config = toml.load(sys.argv[1])
print(extra_config)

# Configuración de simulación
t_end = extra_config['simulation']['log_end']

# Configuración de tanques
data_tanks[-1]['Inputs'][0]['Flow value'] = extra_config['tanks']['flow_value']
data_tanks[-1]['Event Input']['Time']['Max'] = extra_config['tanks']['time']
data_tanks[-1]['Event Input']['Time']['Min'] = extra_config['tanks']['time']
data_tanks[-1]['Event Input']['Vol']['Min'] = extra_config['tanks']['vol']
data_tanks[-1]['Event Input']['Vol']['Min'] = extra_config['tanks']['vol']


# MONTAMOS LA SIMULACION
plant_sim = plant(data_tanks, t_cycle)
plant_sim.simulation(time_end = t_end, user_inputs = data_inputs)

# ANALIZAMOS LOS DATOS
datos  = plant_sim.get_records()
df = plant_sim.get_results(t_end = t_end, t_step = t_step, t_initial = t_initial)

df['Variacion'] = round(df['Volumen dep. almacenam. fin. (L)'] - df['Volumen dep. almacenam. fin. teor. (L)'], 2)
df['Variacion Acum.'] = df.Variacion.rolling(10).sum().round(2) # aqui se aplica una ventana de 10 dias
df2 = df.drop('Fugando combustible', axis=1)
df2['Fugando combustible'] = df['Fugando combustible']
df2.dropna(inplace=True)
df2.reset_index(drop=True)
df2['Tiempo (min)'] = range(1, len(df2)+1)
df2.rename(columns={'Tiempo (min)': 'Tiempo (dia)'}, inplace=True)
df2['Venta (L)'] = - df2['Venta (L)']

# file = 'C:\\Users\\nicok\\OneDrive\\Escritorio\\datos_simulacion.csv'
file = 'datos_simulacion.csv'
df2.to_csv(file, decimal =  ',')
# os.startfile(file)

# plant_sim.graph_volume_records()
# print(df)






