import matplotlib.pyplot as plt
import pandas as pd

# Cargar datos
data = pd.read_csv('C:/Users/DanielC/Documents/ONDAS LABORATORIO/pulsaciones.csv')

# Graficar
plt.figure(figsize=(10,4))
plt.plot(data['Time (ms)'], data['Recording (a.u.)'])
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud (u.a.)')
plt.title('Pulsaciones por interferencia de 440Hz y 500Hz')
plt.grid(True)
plt.show()
print(data)