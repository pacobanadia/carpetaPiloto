"""Predicción de trayectorias en el problema de dos cuerpos con machine learning"""
import numpy as np
import matplotlib.pyplot as plt

"""
definir la funcion que va a predecir la trayectoria de un cuerpo en el espacio,
dada su posición y velocidad iniciales, y el tiempo transcurrido. 
La función debe utilizar un modelo de machine learning previamente entrenado para hacer la predicción.
"""


def predecir_trayectoria(x_0, v_0, t):
    # Cargar el modelo de machine learning previamente entrenado
    modelo = cargar_modelo()
    
    # Crear un vector de características a partir de la posición y velocidad iniciales
    caracteristicas = np.array([x_0[0], x_0[1], v_0[0], v_0[1]])
    # Hacer la predicción utilizando el modelo
    prediccion = modelo.predict(caracteristicas.reshape(1, -1))
    return prediccion
