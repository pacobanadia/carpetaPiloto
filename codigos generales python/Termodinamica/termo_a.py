import numpy as np
import matplotlib.pyplot as plt

# Constantes del gas ideal
R = 8.314   # J/mol·K
n = 1.0     # mol
gamma = 1.4 # Cp/Cv (para gas diatómico, por ejemplo aire)

# Temperaturas
T_H = 600.0  # K (alta)
T_L = 300.0  # K (baja)

# Volúmenes característicos
V1 = 1.0     # m^3
V2 = 2.0     # m^3  (expansión isotérmica)
# En el ciclo de Carnot, las razones entre volúmenes están ligadas por la adiabática:
# T_H * V2^(gamma-1) = T_L * V3^(gamma-1)
V3 = V2 * (T_H/T_L)**(1/(gamma-1))
V4 = V1 * (T_H/T_L)**(1/(gamma-1))

# Presiones (usando PV = nRT)
P1 = n * R * T_H / V1
P2 = n * R * T_H / V2
P3 = n * R * T_L / V3
P4 = n * R * T_L / V4

# --- Proceso 1→2: Isotérmico (a T_H) ---
V_12 = np.linspace(V1, V2, 100)
P_12 = n * R * T_H / V_12

# --- Proceso 2→3: Adiabático (descenso de T_H a T_L) ---
V_23 = np.linspace(V2, V3, 100)
P_23 = P2 * (V2**gamma) / (V_23**gamma)

# --- Proceso 3→4: Isotérmico (a T_L) ---
V_34 = np.linspace(V3, V4, 100)
P_34 = n * R * T_L / V_34

# --- Proceso 4→1: Adiabático (ascenso de T_L a T_H) ---
V_41 = np.linspace(V4, V1, 100)
P_41 = P4 * (V4**gamma) / (V_41**gamma)

# --- Gráfica ---
plt.figure(figsize=(8,6))
plt.plot(V_12, P_12, 'r', label='Isotérmica (T = T_H)')
plt.plot(V_23, P_23, 'b', label='Adiabática (expansión)')
plt.plot(V_34, P_34, 'g', label='Isotérmica (T = T_L)')
plt.plot(V_41, P_41, 'orange', label='Adiabática (compresión)')

# Cierre del ciclo
plt.plot([V1, V1], [P1, P4], 'k--', alpha=0.5)

# Etiquetas y detalles
plt.xlabel('Volumen V [m³]')
plt.ylabel('Presión P [Pa]')
plt.title('Ciclo de Carnot para un gas ideal (diagrama P–V)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
