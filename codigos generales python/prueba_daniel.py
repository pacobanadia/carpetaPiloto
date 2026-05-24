import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.integrate import quad

# 1. Parámetros físicos e iniciales
l = 1.0       # Longitud de la cuerda
c0 = 1.0      # Velocidad de propagación de la onda
N = 20     # Número de términos de la serie de Fourier (armónicos)

# Preparamos el arreglo para los coeficientes a_k
a = np.zeros(N)

# Definimos la función integrando para nuestra condición inicial f(x) = x^2


def funcion_integrando(x, k, l): return (x**2) * np.sin(k * np.pi * x / l)


# 2. Cálculo de los coeficientes de Fourier (a_k)
for k in range(1, N + 1):
    integral = quad(funcion_integrando, 0, l, args=(k, l))[0]
    a[k-1] = (2 / l) * integral  # Aquí multiplicamos la integral por 2/l

# 3. Función que calcula la posición de la cuerda u(x,t)


def calcular_u(x, t):
    suma = 0
    for k in range(1, N + 1):
        # Fórmula completa con la parte espacial (seno) y temporal (coseno)
        termino = a[k-1] * np.sin(k * np.pi * x / l) * \
            np.cos(k * np.pi * c0 * t / l)
        suma += termino
    return suma


# 4. Configuración del espacio y la gráfica
x_puntos = np.linspace(0, l, 100)  # Crea 100 puntos espaciados entre 0 y l
fig, ax = plt.subplots()
ax.set_xlim(0, l)
ax.set_ylim(-1.5, 1.5)             # Límites verticales para ver bien la onda
ax.set_title("Simulación de Cuerda Vibrante: f(x) = x^2")
ax.set_xlabel("Posición (x)")
ax.set_ylabel("Amplitud u(x,t)")
ax.grid(True)

# Creamos la línea vacía que se irá actualizando
linea, = ax.plot([], [], lw=2, color='blue')

# Función para iniciar la animación vacía


def inicializar():
    linea.set_data([], [])
    return linea,

# Función que actualiza la gráfica en cada cuadro (frame)


def animar(i):
    t = i * 0.05  # El tiempo va avanzando en cada cuadro
    u_valores = calcular_u(x_puntos, t)
    linea.set_data(x_puntos, u_valores)
    return linea,


# 5. Ejecución de la animación
ani = animation.FuncAnimation(
    fig, animar, init_func=inicializar, frames=200, interval=30, blit=True)
plt.show()
