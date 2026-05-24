# graficadora de funciones basicas

import matplotlib.pyplot as plt
import numpy as np 
x = np.linspace(0,10,100)
y = np.sin(x)
plt.plot(x,y)
plt.xlabel('Eje X')
plt.ylabel('Eje Y')
plt.title('Grafica de Seno')
plt.grid()

plt.show()
# editar color de la grafica
colorito ="#C7020281"  # Color en formato hexadecimal
# Cambiar el color de la línea
plt.plot(x, y, color=colorito)

