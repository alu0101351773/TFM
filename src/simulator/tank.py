# -*- coding: utf-8 -*-
"""
@author: Yanes Pérez, Nicolás
@version: v1.0
---------------------------------------------------------------------------------------
CLASE Deposito
Clases donde se detalla los tipos de Depositos, atributos y funciones

- Los Depositos activos
    La maquina de estados esta implementada de tal forma que la abre o 
    cierra todas las valvulas de entrada y salida conectadas. 

- Los Depositos pasivos
    solo almacenan el liquido y devuelven el volumen

Añadir los ruido de descarga, la venta y ruido de medida.
---------------------------------------------------------------------------------------
"""

import textwrap
from noise import *
from event import *

class tank(object):
    
    # INICIALIZADOR
    def __init__(self, attr):
        
        # Nombre
        self._name = attr['Name']
        
        # Limite de volumen del Deposito
        self._tank_capacity = attr['Capacity']                # tank volume limit (l)
        self._tank_secure_vol = attr['Security volume max']   # tank volume limit (l)

        # Atributos de estado
        self._volume = 0
        if attr.get('Initial volume'): 
            self._volume = attr['Initial volume']             # current tank volume

        # Atributos externos
        self._tank_controller = None                          # instance of the controller
        self._leak_sens_res =  None                           # leak sensor resolution

        # Atributos ruidos e errores de medidas
        self._noise_vol = noise({"Prob Distr" : "No noise"})
        self._noise_input = noise({"Prob Distr" : "No noise"})
        self._noise_output = noise({"Prob Distr" : "No noise"})
        
        if attr.get('Noise'): 
            if attr['Noise'].get('Volume Measurement'): 
                self._noise_vol = noise(attr['Noise']['Volume Measurement'])
            if attr['Noise'].get('Input'): 
                self._noise_input = noise(attr['Noise']['Input'])
            if attr['Noise'].get('Output'): 
                self._noise_output = noise(attr['Noise']['Output'])


    # FUNCIÓN PRINT
    def __str__(self):
        msg = """\
            TANK : {} 
                |Capacity (l): {}
                |Secure Volume (l): {}
                |Volume (l): {}
                """.format(
                    self.get_name(), 
                    self.get_capacity(),
                    self.get_secure_vol(),
                    self.get_vol()
                    )
        
        return textwrap.dedent(msg)
            
    
    #  Nombre del Deposito
    def get_name(self):
        return self._name
    
    def set_name(self, name):
        self._name = name
        
    
    # Capacidad del Deposito
    def get_capacity(self):
        return self._tank_capacity
    
    def set_capacity(self,capacity):
        self._tank_capacity = capacity
        
        
    # Volumen de seguridad
    def get_secure_vol(self):
        return self._tank_secure_vol

    def set_secure_vol(self,secure_vol):
        self._tank_secure_vol = secure_vol 

    # Obtener el ruido y perturbaciones de las medidas
    def get_noise_vol(self):
        return self._noise_vol
    
    def get_noise_input(self):
        return self._noise_input

    def get_noise_output(self):
        return self._noise_output

            
    # volumen real de deposito
    def get_vol(self):
        return self._volume

    def get_vol_with_noise(self):
        return self.get_noise_vol().set_noise(self._volume)
    
    def set_vol(self, vol):
        self._volume = vol

    def is_empty(self):
        return self.get_vol() <= 0
    
    def is_overflow(self):
        return (self.get_vol() >= self.get_secure_vol())
        
        
    # Controlador asociado al deposito
    def get_controller(self):
        return self._tank_controller         
            
    def set_controller(self, controller):
        self._tank_controller = controller


    # FUNCION QUE COMPRUEBA SI EL DEPOSITO PUEDE RECIBIR EL VOLUMEN DE AGUA DE ENTRADA
    def ready_to_input_vol(self, new_vol):
        return self.get_secure_vol() > (self.get_vol() + new_vol)
        

### CLASE DE DEPOSITO PASIVO
class passive_tank(tank):
    
    # INICIALIZADOR
    def __init__(self, attr):
        super().__init__(attr)
    
    def is_active_tank(self):
        return False

        
    
### CLASE DE DEPOSITO ACTIVO
class active_tank(tank):
    
    # INICIALIZADOR
    def __init__(self, attr):
        super().__init__(attr)

        self._inpipes =  []
        self._outpipes = []

        self._status = 'REBOOT'
        self._previous_st = None

        # eventos de tiempo y volumen
        
        # Eventos
        self._time_input_event = event(attr['Event Input']['Time'])
        self._vol_input_event = event(attr['Event Input']['Vol'])
        self._time_output_event = event(attr['Event Output']['Time'])

        # Cantidad de agua que descargará el deposito cuando la simulación lo diga
        self._next_input_vol = None
        self._next_output_vol = None
        
        # Tiempo en el que se realizará el próximo movimiento del  carga
        self._next_input_time = 0
        self._next_output_time = 0

        # historico entrada y salida del volumen
        self._input_vol = 0
        self._output_vol = 0

    # FUNCIÓN PRINT
    def __str__(self):
        msg = """\
            TANK : {} 
                |Capacity (l): {}
                |Secure Volume (l): {}
                |Volume (l): {}
                |Time input event  attr.: {}
                |Vol. input event  attr.: {}   
                |Time output event  attr.: {}                   
                """.format(
                    self.get_name(), 
                    self.get_capacity(),
                    self.get_secure_vol(),
                    self.get_vol(),
                    str(self.get_time_input_event().get_prob_dist_params()),
                    str(self.get_vol_input_event().get_prob_dist_params()),
                    str(self.get_time_output_event().get_prob_dist_params())
                    )

        return textwrap.dedent(msg)

        
    # HISTORICO DE ENTRADA Y SALIDA VOLUMEN
    def get_input_vol(self):
        return self._input_vol

    def set_input_vol(self):
        for p in self.get_input_pipes():
            self._input_vol += p.get_transf_vol()

    def get_output_vol(self):
        return self._output_vol

    def set_output_vol(self):
        for p in self.get_output_pipes():
            self._output_vol += p.get_transf_vol()

    def is_active_tank(self):
        return True

    def is_leak(self):
        for p in self.get_input_pipes():
            if p.get_valve() == 1:
                return True
        return False

    # VÁLVULAS DE ENTRADA
    def get_input_pipes(self):
        return self._inpipes
        
    def add_input_pipe(self, pipe):
        self._inpipes.append(pipe)


    # VÁLVULAS DE SALIDA
    def get_output_pipes(self):
        return self._outpipes
        
    def add_output_pipe(self, pipe):
        self._outpipes.append(pipe)

        
    # APERTURA Y CIERRE DE VALVULAS DEL DEPÓSITO
    # las valvulas se abren o se cirran todas

    def close_input_valves(self):
        for pip in self.get_input_pipes():
            pip.close_valve()
    
    def close_output_valves(self):
        for pip in self.get_output_pipes():
            pip.close_valve()
    
    def open_input_valves(self):
        for pip in self.get_input_pipes():
            pip.open_valve()
    
    def open_output_valves(self):
        for pip in self.get_output_pipes():
            pip.open_valve()
    
    # ESTADOS DEL DEPÓSITO

    def set_emergency_st(self):
        self._status = 'EMERGENCY'
    
    def set_empty_st(self):
        self._status = 'EMPTY_TANK'
        
    def set_filling_st(self):
        self._status = 'FILLING'

    def set_stop_st(self):
        self._status = 'STOP'
        
    def set_draining_st(self):
        self._status = 'DRAINING'
        
    def set_reboot_st(self):
        self._status = 'REBOOT'
        
    def set_full_st(self):
        self._status = 'FULL_TANK'

    def set_status(self,st):
        self._status = st

    def get_status(self):
        return self._status

    def get_previous_st(self):
        return self._previous_st

    def set_previous_st(self):
        self._previous_st = self.get_status()

    def restore_prev_status(self):
        self.set_status(self.get_previous_st())
    
    
    # COMPROBACIÓN DEL ESTADO

    def is_reboot_st(self):
        return self._status == 'REBOOT'
    
    def is_emergency_st(self):
        return self._status == 'EMERGENCY'

    def is_stop_st(self):
        return self._status == 'STOP'
        
    def is_empty_st(self):
        return self._status == 'EMPTY_TANK'

    def is_draining_st(self):
        return self._status == 'DRAINING'
        
    def is_full_st(self):
        return self._status == 'FULL_TANK'
            
    def is_filling_st(self):
        return self._status == 'FILLING'


    # GET DE EVENTOS DEL TANQUE
   
    # EVENTOS DE TIEMPO Y VOLUMEN
    def get_vol_input_event(self):
        return self._vol_input_event

    def get_time_input_event(self):
        return self._time_input_event

    def get_time_output_event(self):
        return self._time_output_event


    # GENERACION VALORES ALEATORIOS DE VOLUMEN

    def get_next_input_vol(self):
        return self._next_input_vol

    def set_next_input_vol(self):
        self._next_input_vol = 0
        self._next_input_vol += self.get_vol_input_event().get_prob_dist()
        
        
    # GENERACION VALORES ALEATORIOS DE TIEMPO
    def get_next_input_time(self):
        return self._next_input_time

    def set_next_input_time(self, tsimulation):
        self._next_input_time = tsimulation
        self._next_input_time += self.get_time_input_event().get_prob_dist()

    def get_next_output_time(self):
        return self._next_output_time

    def set_next_output_time(self, tsimulation):
        self._next_output_time = tsimulation
        self._next_output_time += self.get_time_output_event().get_prob_dist()

    
    # ACTUALIZACIÓN DEL ESTADO
    # retorna True si se encuenta en estado de emergencia
    def update_status(self, tsimulation, start_begin): 
        
        # CONDICIÓN PARA PASAR A ESTADO DE EMERGENCIA
        if self.get_controller().is_emergency_st():
            self.set_emergency_st()
        
        elif self.is_overflow() & (not self.is_reboot_st()) :
            self.set_emergency_st()
        
        # CONDICIÓN PARA PASAR A ESTADO DE PARADA
        elif (self.get_controller().is_stop_st()) and (not self.is_stop_st()):
            self.set_previous_st()
            self.set_stop_st()

        ## COMPORTAMIENTO DEL DEPÓSTIO

        # ACTUACIÓN EN CASO DE ESTADO DE PARADA
        if self.is_stop_st():
            self.close_input_valves()
            self.close_output_valves()
            
            if not self.get_controller().is_stop_st():
                self.restore_prev_status()    
        
        # ACTUACIÓN EN CASO DE ESTADO DE DEPÓSITO VACIO
        if self.is_empty_st():
            self.close_input_valves()
            self.close_output_valves()

            if (tsimulation >= self.get_next_input_time()):
                self.set_filling_st()
            
        
        # ACTUACIÓN EN CASO DE ESTADO DE LLENANDO DEPÓSITO
        if self.is_filling_st():
            self.open_input_valves()
            self.close_output_valves()

            if self.get_vol() >= self.get_next_input_vol():
                self.set_full_st()
                self.set_next_output_time(tsimulation)

        # ACTUACIÓN EN CASO DE ESTADO DE DESPÓSITO LLENO
        if self.is_full_st():
            self.close_input_valves()
            self.close_output_valves()

            if (tsimulation >= self.get_next_output_time()):
                self.set_draining_st()
        
        # ACTUACIÓN EN CASO DE VACIADO DE DEPÓSITO
        if self.is_draining_st():
            self.close_input_valves()
            self.open_output_valves()

            if self.is_empty():
                self.set_empty_st()
                self.set_next_input_vol()
                self.set_next_input_time(tsimulation)

        # ACTUACIÓN EN CASO DE ESTADO DE EMERGENCIA
        if self.is_emergency_st() :
            self.close_input_valves()
            self.open_output_valves()

            if not self.get_controller().is_emergency_st():
                self.set_reboot_st()
            else:
                return True

        # ACTUACIÓN EN CASO DE ESTADO DE REINICIO
        if self.is_reboot_st():
            self.close_input_valves()
            self.open_output_valves()

            if start_begin and self.is_empty():
                self.set_empty_st()
                self.set_next_input_vol()
                self.set_next_input_time(tsimulation)
        
        return False

    # FUNCION DE TRANSFERENCIA DE VOLUMEN DEL PROPIO DEPÓSITO
    def transfer_vol(self):
        t_cycle = self.get_controller().get_time_cycle()
        for p in self.get_input_pipes() + self.get_output_pipes():
            p.transfer_vol()

        # historico de E/S volumen
        self.set_input_vol()
        self.set_output_vol()

    




    
    