# -*- coding: utf-8 -*-
"""
@author: Yanes Pérez, Nicolás
@version: v1.0
---------------------------------------------------------------------------------------
CLASS PLANT
La instancia de este objeto recibo una lista de atributos para crear los objetos tanques
separados.

Apuntes:
- El ruido se añade a partir de la simulacion
---------------------------------------------------------------------------------------
"""

import matplotlib.pyplot as plt
import pandas as pd

from tank import *
from pipe import *
from controller import *

class plant(object):

    # INICIALIZADOR
    def __init__(self, plant_info, t_cycle):
        
        self._time_cycle = t_cycle
        self._time_simulation = 0


        self._tanks = {}
        self._in_pipes = []
        self._out_pipes = []

        self._records = {}

        
        # Creamos todos los tanques y los clasificamos por su nombre en un diccionario
        for attr in plant_info:
            if ('Inputs' in attr.keys()) or ('Outputs' in attr.keys()):
                self._tanks[attr['Name']] = active_tank(attr)
            else:
                self._tanks[attr['Name']] = passive_tank(attr)

            print(self._tanks[attr['Name']])

        # Creamos lista de tuberia
        for attr in plant_info: 

            if not ('Inputs' in attr.keys()):
                continue

            for pattr in attr.get('Inputs'):
                ini = self._tanks.get(pattr.get('Name'))
                end = self._tanks.get(attr.get('Name'))
                name = 'PIPE - INPUT {}'.format(end.get_name()) 
                time_cycle = self._time_cycle

                self._in_pipes.append(pipe(name, ini, end, pattr, time_cycle))
                print(self._in_pipes[-1])

            if not ('Outputs' in attr.keys()):
                continue

            for pattr in attr.get('Outputs'):
                ini = self._tanks.get(attr.get('Name'))
                end = self._tanks.get(pattr.get('Name'))
                name =  'PIPE - OUTPUT {}'.format(ini.get_name())    

                self._out_pipes.append(pipe(name, ini, end, pattr, time_cycle))
                print(self._out_pipes[-1])

        # Introducimos las tuberias con sus respectivos depostivos activos
        for pip in self._in_pipes:
            name_tank = pip.get_end().get_name()
            self._tanks[name_tank].add_input_pipe(pip)
        
        for pip in self._out_pipes:
            name_tank = pip.get_ini().get_name()
            self._tanks[name_tank].add_output_pipe(pip)

        # Creamos el controlador de la planta y lo conectamos a los tanques
        self._controller = controller(self._time_cycle)

        for t in self._tanks.values():
            if (hasattr(t, '_inpipes')) or (hasattr(t, '_outpipes')):
                self._controller.add_active_tanks(t)
            else:
                self._controller.add_passive_tanks(t)

        print(self._controller)

        # Introducimos el controlador en los tanques
        for t in self._tanks.values():
            t.set_controller(self._controller)

    # FUNCIONES DE OBTENCIÓN Y MODIFICACION DE DE ATRIBUTOS

    def get_time_cycle(self):
        return self._time_cycle

    def get_time_simulation(self):
        return self._time_simulation

    def set_time_simulation(self, new_time):
        self._time_simulation = new_time

    def get_time_end(self):
        return self._time_end

    def get_controller(self):
        return self._controller

    def get_tanks(self):
        return self._tanks

    def get_active_tanks(self):
        return self.get_controller().get_active_tanks()

    def get_passive_tanks(self):
        return self.get_controller().get_passive_tanks()

    def get_all_tanks(self):
        return self.get_active_tanks() + self.get_passive_tanks()

    def get_inputs_pipes(self):
        return self._in_pipes

    def get_outputs_pipes(self):
        return self._out_pipes

    def get_records(self):
        return self._records

    def add_record(self,key,data):
        if not (key in self._records.keys()):
            self._records[key] = []
        self._records[key].append(data)

    # FUNCIÓN DE REGISTRO DE MEDIDA DE LA SIMULACION

    def record_plant(self):

        # tiempo
        self.add_record('time (min)', self.get_time_simulation())      
        
        # volumen de los tanques 
        for t in self.get_passive_tanks():
            self.add_record(t.get_name(), t.get_vol_with_noise())

        for t in self.get_active_tanks():
            self.add_record(t.get_name(), t.get_vol_with_noise())
            self.add_record(t.get_name() + ' - input vol', t.get_input_vol())
            self.add_record(t.get_name() + ' - output vol', t.get_output_vol())

            if t.get_name() == "Leak_tank":
                if t.is_leak():
                    self.add_record(t.get_name() + ' - LEAK STATUS', 1)
                else:
                    self.add_record(t.get_name() + ' - LEAK STATUS', 0)


        # botones del cuadro de mandos
        self.add_record('start_bt',self.get_controller().get_start_bt())
        self.add_record('stop_bt',self.get_controller().get_stop_bt())
        self.add_record('emergency_bt',self.get_controller().get_emergency_bt())
        self.add_record('dial',self.get_controller().get_dial())

        # estado del controlador
        self.add_record('status_controller',self.get_controller().get_status())


    # ACTUALIZA LOS VOLUMENES DE LOS DEPÓSITOS
    def update_plant(self):
        for t in self.get_active_tanks():
            t.transfer_vol()

     
    def simulation(self, time_end, user_inputs):

        self.get_controller().set_user_inputs(user_inputs)
        
        while time_end >= self.get_time_simulation():
            self.get_controller().apply_user_inputs(self.get_time_simulation())
            self.record_plant()
            self.get_controller().update_controller(self.get_time_simulation())
            self.update_plant()
            
            new_time = self.get_time_simulation() + self.get_time_cycle()
            self.set_time_simulation(new_time)


    # representar el volumen de los tanques
    def graph_volume_records(self):
        
        # datos
        datos = self.get_records()

        x = datos['time (min)']
        ly = []
        lname = []

        for t in self.get_all_tanks():       
            if t.get_name() in ['Storage_tank', 'Dispenser 1', 'Dispenser 2', 'Refill_tank']:                         
                ly.append(datos[t.get_name()])
                lname.append(t.get_name())

        # contruimos la cantidad de graficas que se requiere
        fig, axs = plt.subplots(len(ly), 1)

        for i in range(len(ly)):
            y = ly[i]
            title = lname[i]
            axs[i].plot(x,y)
            axs[i].set_title(title)
            axs[i].set_xlim([0, max(x)])
            axs[i].set_ylim([min(y), max(y)])


        for ax in axs.flat:
            ax.set(xlabel='time (min)', ylabel='Volume (l)')

        # Esconde los ticks de la grafica en el eje x
        for ax in axs.flat:
            ax.label_outer()

        plt.show()

    # SALIDA DE LA SIMULACIÓN
    # EL VOLUMEN AL FINAL DEL PERIODO COINCIDIRA AL INICIO

    def get_results(self, t_end = 100, t_step = 10, t_initial = 0):
        records = self.get_records()
        l_times = []            # TIEMPO SIMULACIÓN
        l_vol_i = []            # INICIO PERIODO DEL VOLUMEN DEL --TANQUE PRINCIPAL-- 
        l_venta = []            # VENTA DURANTE EL PERIODO COMPLETO (TOTAL)
        l_input_vol = []        # LO QUE ENTRA EN EL DEPOSITO DE ALMACENAMIENTO (L)
        l_vol_f1 = []           # VOLUMEN DEL DEPOSITO ALMACENAMIENTO AL FINAL DEL PERIODO CALCULADO   
        l_vol_f2 = []           # VOLUMEN DEL DEPOSITO ALMACENAMIENTO AL FINAL DEL PERIODO (T_STEP)
        l_leak = []             # 0/1 EL DEPÓSITO DE ALMACENAMIENTO ESTÁ 

        for t in range(t_initial, t_end - 1, t_step):
            index_i = records['time (min)'].index(t)
            index_f = records['time (min)'].index(t + t_step)
            
            l_times.append(t + t_step)
            l_vol_i.append(round(records['Storage_tank'][index_i], 2))
            l_vol_f2.append(round(records['Storage_tank'][index_f], 2))
            
            # calculo de la venta (salida de los dispensadores)
            venta = 0
            for name in records.keys():
                if ('Dispenser' in name) and not('-' in name):
                    venta += (records[name + ' - input vol'][index_f] - records[name + ' - input vol'][index_i])
            
            l_venta.append(round(venta, 2))

            # calculo de la entrada en el deposito
            for name in records.keys():
                if ('Refill_tank' in name) and not('-' in name):
                    input_vol = records[name + ' - output vol'][index_f] - records[name + ' - output vol'][index_i]
            
            l_input_vol.append(round(input_vol, 2))

            l_vol_f1.append(round(l_vol_i[-1] - l_venta[-1] + l_input_vol[-1], 2))

            if 1 in records['Leak_tank - LEAK STATUS'][index_i:index_f]:
                l_leak.append(1)
            else:
                l_leak.append(0)

        data = {
            'Tiempo (min)': l_times,
            'Volumen dep. almacenam. ini. (L)': l_vol_i,
            'Venta (L)': l_venta,
            'Llenado dep. almacenam. (L)': l_input_vol,
            'Volumen dep. almacenam. fin. teor. (L)': l_vol_f1,
            'Volumen dep. almacenam. fin. (L)': l_vol_f2,
            'Fugando combustible': l_leak
        }

        return pd.DataFrame.from_dict(data)

        








         

