# modelo_senoidal.py
# Autor: Daniel Cano Duque
# Proyecto PyTorch 2025 – Entregable 1
# Inciso 1: Fundamentos – Clases, métodos y construcción de una red neuronal simple

# Importa la librería principal de PyTorch para trabajar con tensores y redes neuronales
import torch

# Importa el módulo nn (neural network) de PyTorch que contiene capas y funciones de activación
import torch.nn as nn

# Importa NumPy para operaciones matemáticas y generación de arrays numéricos
import numpy as np

# Importa Matplotlib para visualizar gráficos y datos
import matplotlib.pyplot as plt

# Define una clase llamada ModeloSenoidal que encapsulará toda la funcionalidad del modelo
class ModeloSenoidal:
    """
    Clase base para generar datos y construir un modelo neuronal
    que aprenda la relación y = sin(x).
    """

    # Método constructor que se ejecuta cuando se crea una instancia de la clase
    def __init__(self):
        # Inicializa el atributo 'modelo' en None (aún no se ha construido la red neuronal)
        self.modelo = None
        # Inicializa el atributo 'x_entrenamiento' en None (aún no se han generado los datos de entrada)
        self.x_entrenamiento = None
        # Inicializa el atributo 'y_entrenamiento' en None (aún no se han generado los datos de salida)
        self.y_entrenamiento = None

    # Define un método para generar datos sintéticos de la función seno
    # Los parámetros n_samples (número de puntos) y rango (intervalo) tienen valores por defecto
    def generar_datos(self, n_samples: int = 1000, rango: tuple = (0, 2 * np.pi)):
        """
        Genera datos (x, y) donde y = sin(x), dentro del rango dado.
        Los datos se convierten a tensores de PyTorch.
        """
        # Crea un array de 1000 valores espaciados uniformemente entre 0 y 2π (rango por defecto)
        x = np.linspace(rango[0], rango[1], n_samples)
        # Calcula el seno de cada valor de x, obteniendo los valores de y
        y = np.sin(x)

        # Convierte el array x de NumPy a un tensor de PyTorch con tipo de dato float32
        # .view(-1, 1) reorganiza el tensor a una matriz columna (n_samples filas, 1 columna)
        self.x_entrenamiento = torch.tensor(x, dtype=torch.float32).view(-1, 1)
        # Convierte el array y de NumPy a un tensor de PyTorch con tipo de dato float32
        # .view(-1, 1) reorganiza el tensor a una matriz columna (n_samples filas, 1 columna)
        self.y_entrenamiento = torch.tensor(y, dtype=torch.float32).view(-1, 1)

        # Retorna los tensores generados para que puedan ser usados fuera del método
        return self.x_entrenamiento, self.y_entrenamiento

    # Define un método para construir la arquitectura de la red neuronal
    def construir_modelo(self):
        """
        Crea una red neuronal simple con una capa oculta y activación Tanh.
        """
        # Crea una red neuronal secuencial (las capas se aplican una tras otra)
        self.modelo = nn.Sequential(
            # Primera capa Linear: recibe 1 entrada (valor de x) y produce 10 salidas (neuronas ocultas)
            nn.Linear(1, 10),
            # Función de activación Tanh aplicada a las 10 neuronas ocultas (introduce no-linealidad)
            nn.Tanh(),
            # Segunda capa Linear: recibe 10 entradas (de las neuronas ocultas) y produce 1 salida (valor de y)
            nn.Linear(10, 1)
        )

        # Retorna la red neuronal construida para poder usarla fuera del método
        return self.modelo


# Bloque que se ejecuta solo si este archivo se ejecuta directamente (no si se importa)
if __name__ == "__main__":
    # Crea una instancia (objeto) de la clase ModeloSenoidal
    modelo = ModeloSenoidal()
    # Llama al método generar_datos() que genera 1000 pares (x, y) con y = sin(x)
    # Guarda los datos en las variables x e y
    x, y = modelo.generar_datos()
    # Llama al método construir_modelo() que crea la arquitectura de la red neuronal
    # Guarda la red en la variable red
    red = modelo.construir_modelo()

    # Imprime en consola la forma (dimensiones) de los tensores generados
    print("Datos generados:", x.shape, y.shape)
    # Imprime en consola el mensaje "Estructura del modelo:"
    print("Estructura del modelo:")
    # Imprime la arquitectura completa de la red neuronal mostrando todas sus capas
    print(red)