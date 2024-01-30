# -*- coding: utf-8 -*-
"""
@author: Yanes Pérez, Nicolás
@version: v1.0
---------------------------------------------------------------------------------------
CLASE TUBERIA

---------------------------------------------------------------------------------------
"""

import textwrap

from flow import *
from event import *
from tank import *

class pipe(object):
    
    # INICIALIZADOR
    def __init__(self, name, ini, end, attr, time_cycle):

        self._name = name
                
        self._ini = ini                          # El tanque que vacia
        self._end = end                          # El tanque que llena
                    
        self._flow = flow(attr, ini, time_cycle) # Caudal de la tuberia    
        
        self._valve = 0                          # 0 (cerrado)/1 (abierto)

        # ultimo volumen transferido
        self._transfer_vol = 0                   # utilizado para el data log 


    # FUNCION PRINT
    def __str__(self):
        name = self.get_name()
        name_ini = self.get_ini().get_name()
        name_end = self.get_end().get_name()
        flow_type = self.get_flow().get_flow_type()
        flow_value = self.get_flow().get_flow_value()

        if 'PIPE - INPUT' in name:
            msg = """\
                {}
                    |from: '{}'
                    |flow type: '{}'
                    |flow value: {}
                """.format(name, name_ini,flow_type,flow_value)

        elif 'PIPE - OUTPUT' in name:
            msg = """\
                {}
                    |to: '{}'
                    |flow type: '{}'
                    |flow value: {}                    
                """.format(name, name_end,flow_type,flow_value)
        else:
            msg = "-- ERROR PIPE --" 

        return textwrap.dedent(msg)
        
    
    def get_name(self):
        return self._name


    # TANQUE CONECTADO QUE VACIA
    def get_ini(self):
        return self._ini
    
    def set_ini(self, tank):
        self._ini = tank
        
    # TANQUE CONECTADO QUE LLENA    
    def get_end(self):
        return self._end
    
    def set_end(self, tank):
        self._end = tank


    # CAUDAL DE LA TUBERIA
    def get_flow(self):
        return self._flow

    def set_flow(self,new_flow):
        self._flow = new_flow

        
    # APERTURA O CIERRE DE LA VALVULA
    def get_valve(self):
        return self._valve
    
    def open_valve(self):
        self._valve = 1
        
    def close_valve(self):
        self._valve = 0

    # SET / GET VOLUMEN TRASFERIDO
    def get_transf_vol(self):
        return self._transfer_vol

    def set_transf_vol(self,vol):
        self._transfer_vol = vol

    
        
    # TRANSFERENCIA DE VOLUMEN 
    def transfer_vol(self):
        
        if self.get_valve() == 1:
            # para en caso que el volumen del deposito sea menor al volumen a transferir
            volume = min(self.get_ini().get_vol(), self.get_flow().get_vol())

            if volume == 0:
                self.set_transf_vol(0) # grabamos la ultima transferencia de volumen
                return None


            if self.get_end().ready_to_input_vol(volume):
                
                #aplicamos error al volumen para que la tuberia no se comporte de forma perfecta
                if self.get_ini().is_active_tank():
                    vol_error = self.get_ini().get_noise_output().set_noise(volume)
                else:
                    vol_error = self.get_end().get_noise_input().set_noise(volume)


                # aplicacmos la transferencia de volumen
                vol_ini = self.get_ini().get_vol() - vol_error
                self.get_ini().set_vol(vol_ini)

                vol_end =  self.get_end().get_vol() + vol_error
                self.get_end().set_vol(vol_end)

                self.set_transf_vol(volume) # guardamos el ideal marcado 
            else:
                self.set_transf_vol(0) 
        
        else:
            self.set_transf_vol(0) 
                


            
    
    

        
        