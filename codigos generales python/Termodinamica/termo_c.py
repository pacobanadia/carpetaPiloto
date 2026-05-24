import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Datos de la tabla
distancia = np.array([5.40, 6.00, 7.30, 8.43, 9.00, 12.15, 16.00])  # metros
tiempo = np.array([36, 49, 56, 64, 81, 107, 135])  # nanosegundos

# 1. Regresión lineal
pendiente, intercepto, r_value, p_value, std_err = stats.linregress(tiempo, distancia)

# 2. Crear línea de regresión
tiempo_ajuste = np.linspace(min(tiempo), max(tiempo), 100)
distancia_ajuste = pendiente * tiempo_ajuste + intercepto

# 3. Calcular coeficiente de determinación R²
r_cuadrado = r_value**2

# 4. Crear la gráfica
plt.figure(figsize=(12, 8))

# Puntos experimentales
plt.scatter(tiempo, distancia, color='blue', s=80, zorder=5, label='Datos experimentales')

# Línea de regresión
plt.plot(tiempo_ajuste, distancia_ajuste, 'r-', linewidth=2, 
         label=f'Regresión lineal: y = {pendiente:.4f}x + {intercepto:.4f}')

# Personalizar la gráfica
plt.xlabel('Tiempo (ns)', fontsize=12)
plt.ylabel('Distancia (m)', fontsize=12)
plt.title('Regresión Lineal: Distancia vs Tiempo', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=11)

# Añadir ecuación y estadísticas en el gráfico
textstr = f'y = {pendiente:.4f}x + {intercepto:.4f}\nR² = {r_cuadrado:.4f}\nn = {len(tiempo)} puntos'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
plt.text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=11,
         verticalalignment='top', bbox=props)

plt.tight_layout()
plt.show()

# 5. Mostrar resultados detallados
print("=" * 50)
print("RESULTADOS DE LA REGRESIÓN LINEAL")
print("=" * 50)
print(f"Ecuación de la recta: d = {pendiente:.6f}·t + {intercepto:.4f}")
print(f"Pendiente (velocidad): {pendiente:.6f} m/ns")
print(f"Intercepto: {intercepto:.4f} m")
print(f"Coeficiente de correlación (r): {r_value:.4f}")
print(f"Coeficiente de determinación (R²): {r_cuadrado:.4f}")
print(f"Error estándar: {std_err:.6f}")

# 6. Convertir velocidad a m/s
velocidad_ms = pendiente * 1e9  # Convertir m/ns a m/s
print(f"\nVelocidad en m/s: {velocidad_ms:.2e} m/s")

# 7. Predicciones
print(f"\nPREDICCIONES:")
print(f"Para t = 100 ns → d = {pendiente*100 + intercepto:.2f} m")
print(f"Para d = 10 m → t = {(10 - intercepto)/pendiente:.2f} ns")

# 8. Tabla de residuales
print(f"\nANÁLISIS DE RESIDUALES:")
print("Tiempo(ns) Distancia(m) Predicción Residual")
print("-" * 45)
for i in range(len(tiempo)):
    pred = pendiente * tiempo[i] + intercepto
    residual = distancia[i] - pred
    print(f"{tiempo[i]:8.0f} {distancia[i]:11.2f} {pred:9.3f} {residual:8.3f}")