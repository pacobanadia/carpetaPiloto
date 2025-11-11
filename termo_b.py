import numpy as np
import matplotlib.pyplot as plt

# Parámetros para una campana de saturación simplificada
V_liq = np.linspace(0.001, 0.01, 100)
V_vap = np.linspace(0.01, 0.1, 100)

# Curvas de saturación (presión de saturación decrece con volumen)
P_sat_liq = 1 / (V_liq ** 0.3) * 1e5  # curva aproximada
P_sat_vap = 1 / (V_vap ** 1.0) * 1e4

# Puntos del ciclo de Carnot
# Isoterma alta (vaporización)
V1, V2 = 0.01, 0.08
P_H = 2.5e5
V_12 = np.linspace(V1, V2, 50)
P_12 = np.ones_like(V_12) * P_H

# Adiabática de vapor (expansión)
V3 = 0.09
P_23 = np.linspace(P_H, 1.0e5, 50)
V_23 = np.linspace(V2, V3, 50)

# Isoterma baja (condensación)
P_L = 1.0e5
V4 = 0.02
V_34 = np.linspace(V3, V4, 50)
P_34 = np.ones_like(V_34) * P_L

# Adiabática de líquido (compresión)
V_41 = np.linspace(V4, V1, 50)
P_41 = np.linspace(P_L, P_H, 50)**1.0

# Gráfico
plt.figure(figsize=(9,6))

# Curvas de saturación (campana)
plt.plot(V_liq, P_sat_liq, 'gray', lw=2)
plt.plot(V_vap, P_sat_vap, 'gray', lw=2)

# Ciclo de Carnot
plt.plot(V_12, P_12, 'r', label='Isotérmica alta (vaporización, Qₕ entra)')
plt.plot(V_23, P_23, 'b', label='Adiabática (expansión)')
plt.plot(V_34, P_34, 'g', label='Isotérmica baja (condensación, Qₗ sale)')
plt.plot(V_41, P_41, 'orange', label='Adiabática (compresión)')

# Cierre del ciclo
plt.plot([V1, V1], [P_L, P_H], 'k--', alpha=0.6)

# Etiquetas y detalles
plt.xlabel('Volumen específico V [m³/kg]')
plt.ylabel('Presión P [Pa]')
plt.title('Ciclo de Carnot para un líquido en equilibrio con su vapor (diagrama P–V)')
plt.legend()
plt.grid(True)
plt.ylim(0, 3e5)
plt.xlim(0, 0.1)
plt.tight_layout()
plt.show()
