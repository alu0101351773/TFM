# -*- coding: utf-8 -*-
"""
@author: Yanes Pérez, Nicolás
@version: v1.0
---------------------------------------------------------------------------------------
CLASE RUIDO
    En esta clase definimos los tipos de ruidos producidos en las medidas de los sensores
    https://stackoverflow.com/questions/14058340/adding-noise-to-a-signal-in-python

"""
import numpy as np

class noise(object):
    
    # INICIALIZADOR
    def __init__(self, attr):
        # Parametros del ruido de medida
        self._params = attr

    def get_params(self):
        return self._params

    def get_type(self):
        return self._params['Prob Distr']

    def set_noise(self, value):
        type = self.get_type()
        params = self.get_params()

        if type == "Normal Distribution":
            mean =  params['Mean']
            std_desv = params['Standard desviation']
            noise_signal = np.random.normal(mean, std_desv, 1)[0]
            return abs(value + noise_signal)
        
        elif type == "No noise":
            return value
        
        else:
            return value

    