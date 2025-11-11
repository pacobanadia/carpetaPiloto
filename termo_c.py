import matplotlib.pyplot as plt
import numpy as np
import os

# Directorio para guardar las imágenes
output_dir = "output_diagrams"
os.makedirs(output_dir, exist_ok=True)

# Configuración de estilo
plt.style.use('seaborn-v0_8-whitegrid')

# --- Función para dibujar el ciclo de Carnot genérico ---
def draw_carnot_cycle(ax, x_label, y_label, title, x_range, y_range,
                      isotherm_func_H, isotherm_func_C,
                      adiabatic_func_1, adiabatic_func_2,
                      point_labels=['1', '2', '3', '4'],
                      reverse_x=False, reverse_y=False):
    """
    Dibuja un ciclo de Carnot genérico.

    :param ax: Eje de Matplotlib.
    :param x_label: Etiqueta del eje X.
    :param y_label: Etiqueta del eje Y.
    :param title: Título del gráfico.
    :param x_range: Rango de valores para X.
    :param y_range: Rango de valores para Y.
    :param isotherm_func_H: Función para la isoterma caliente (TH).
    :param isotherm_func_C: Función para la isoterma fría (TC).
    :param adiabatic_func_1: Función para la adiabática 1 (TC -> TH).
    :param adiabatic_func_2: Función para la adiabática 2 (TH -> TC).
    :param point_labels: Etiquetas para los puntos del ciclo.
    :param reverse_x: Si el eje X debe ser invertido (e.g., para M).
    :param reverse_y: Si el eje Y debe ser invertido (e.g., para E).
    """
    # Puntos del ciclo (cualitativos)
    # 1: Inicio (TC, V_min)
    # 2: Fin de adiabática 1 (TH, V_intermedio)
    # 3: Fin de isoterma H (TH, V_max)
    # 4: Fin de adiabática 2 (TC, V_intermedio_2)

    # Definición de los puntos para el gráfico cualitativo
    # Usaremos valores que se ajusten a las funciones
    
    # Puntos de referencia (ajustar según la función)
    x1, y1 = x_range[0], y_range[1] * 0.7
    x2, y2 = x_range[0] * 1.5, y_range[1]
    x3, y3 = x_range[1], y_range[1]
    x4, y4 = x_range[1] * 0.7, y_range[1] * 0.7

    # Ajuste para el gas ideal (PV)
    if title == "(a) Gas Ideal (Diagrama P-V)":
        x1, y1 = 1.0, 3.0  # Punto 1 (TC)
        x2, y2 = 1.5, 5.0  # Punto 2 (TH)
        x3, y3 = 3.0, 2.5  # Punto 3 (TH)
        x4, y4 = 2.0, 1.6  # Punto 4 (TC)
        
        # Generar curvas
        V_12 = np.linspace(x1, x2, 50)
        P_12 = adiabatic_func_1(V_12, x1, y1, x2, y2) # Adiabática 1 (TC -> TH)
        
        V_23 = np.linspace(x2, x3, 50)
        P_23 = isotherm_func_H(V_23, x2, y2, x3, y3) # Isoterma H (TH)
        
        V_34 = np.linspace(x3, x4, 50)
        P_34 = adiabatic_func_2(V_34, x3, y3, x4, y4) # Adiabática 2 (TH -> TC)
        
        V_41 = np.linspace(x4, x1, 50)
        P_41 = isotherm_func_C(V_41, x4, y4, x1, y1) # Isoterma C (TC)
        
        # Curvas de referencia (para mostrar la forma)
        V_iso_H = np.linspace(x2*0.8, x3*1.2, 100)
        P_iso_H_ref = isotherm_func_H(V_iso_H, x2, y2, x3, y3) * (y2/isotherm_func_H(x2, x2, y2, x3, y3))
        
        V_iso_C = np.linspace(x1*0.8, x4*1.2, 100)
        P_iso_C_ref = isotherm_func_C(V_iso_C, x4, y4, x1, y1) * (y1/isotherm_func_C(x1, x4, y4, x1, y1))
        
        # Dibujar curvas de referencia (isotermas)
        ax.plot(V_iso_H, P_iso_H_ref, 'k--', alpha=0.3, label=r'$T_H$ (Referencia)')
        ax.plot(V_iso_C, P_iso_C_ref, 'k--', alpha=0.3, label=r'$T_C$ (Referencia)')
        
        # Dibujar el ciclo
        ax.plot(V_12, P_12, 'r-', linewidth=2, label='Adiabática 1 (1->2)')
        ax.plot(V_23, P_23, 'b-', linewidth=2, label='Isoterma H (2->3)')
        ax.plot(V_34, P_34, 'r-', linewidth=2, label='Adiabática 2 (3->4)')
        ax.plot(V_41, P_41, 'b-', linewidth=2, label='Isoterma C (4->1)')
        
        # Puntos
        ax.plot([x1, x2, x3, x4], [y1, y2, y3, y4], 'ko', markersize=5)
        
        # Etiquetas de los puntos
        ax.text(x1 * 0.9, y1 * 1.05, point_labels[0], fontsize=12, ha='right')
        ax.text(x2 * 1.05, y2 * 1.0, point_labels[1], fontsize=12, ha='left')
        ax.text(x3 * 1.0, y3 * 1.05, point_labels[2], fontsize=12, ha='left')
        ax.text(x4 * 0.9, y4 * 0.9, point_labels[3], fontsize=12, ha='right')
        
        # Flechas de dirección
        ax.annotate('', xy=(V_12[25], P_12[25]), xytext=(V_12[24], P_12[24]),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='r', linewidth=1.5))
        ax.annotate('', xy=(V_23[25], P_23[25]), xytext=(V_23[24], P_23[24]),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='b', linewidth=1.5))
        ax.annotate('', xy=(V_34[25], P_34[25]), xytext=(V_34[24], P_34[24]),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='r', linewidth=1.5))
        ax.annotate('', xy=(V_41[25], P_41[25]), xytext=(V_41[24], P_41[24]),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='b', linewidth=1.5))
        
        ax.set_xlim(0.8, 3.5)
        ax.set_ylim(1.0, 5.5)
        
    # Ajuste para el líquido-vapor (PV)
    elif title == "(b) Líquido-Vapor (Diagrama P-V)":
        # Puntos: 1 (Líquido saturado, TC), 2 (Vapor saturado, TC), 3 (Vapor saturado, TH), 4 (Líquido saturado, TH)
        # En la región de coexistencia, las isotermas son horizontales (P=cte)
        
        # Puntos cualitativos
        V_liq_C, P_C = 1.0, 2.0  # Punto 1 (Líquido saturado, TC)
        V_vap_C, P_C = 4.0, 2.0  # Punto 4 (Vapor saturado, TC)
        V_liq_H, P_H = 1.5, 4.0  # Punto 2 (Líquido saturado, TH)
        V_vap_H, P_H = 5.0, 4.0  # Punto 3 (Vapor saturado, TH)
        
        # Curva de saturación (cualitativa)
        V_sat = np.linspace(0.8, 5.2, 100)
        P_sat = 0.5 * (V_sat - 3.0)**2 + 2.0
        P_sat[V_sat < 3.0] = 0.5 * (V_sat[V_sat < 3.0] - 3.0)**2 + 2.0
        P_sat[V_sat > 3.0] = 0.5 * (V_sat[V_sat > 3.0] - 3.0)**2 + 2.0
        
        # Ajuste de la curva de saturación para que pase por los puntos
        V_sat_x = [V_liq_C, V_liq_H, 3.0, V_vap_H, V_vap_C]
        P_sat_y = [P_C, P_H, 5.0, P_H, P_C]
        
        # Curva de saturación (campana)
        V_campana = np.linspace(0.8, 5.2, 100)
        P_campana = np.interp(V_campana, [1.0, 1.5, 3.0, 5.0, 4.0], [2.0, 4.0, 5.0, 4.0, 2.0])
        
        ax.plot(V_campana, P_campana, 'k--', alpha=0.5, label='Curva de Saturación')
        
        # Puntos del ciclo
        # 1 -> 2: Isoterma C (P=cte)
        # 2 -> 3: Adiabática (V, P aumentan)
        # 3 -> 4: Isoterma H (P=cte)
        # 4 -> 1: Adiabática (V, P disminuyen)
        
        # Puntos ajustados para el ciclo
        x1, y1 = 1.5, 2.0  # Líquido saturado (TC)
        x2, y2 = 4.5, 2.0  # Vapor saturado (TC)
        x3, y3 = 4.0, 4.0  # Vapor saturado (TH)
        x4, y4 = 2.0, 4.0  # Líquido saturado (TH)
        
        # Isoterma C (1 -> 2)
        ax.plot([x1, x2], [y1, y2], 'b-', linewidth=2, label='Isoterma C (1->2)')
        
        # Adiabática 1 (2 -> 3) - Cualitativa, pendiente negativa en PV
        V_23 = np.linspace(x2, x3, 50)
        P_23 = np.interp(V_23, [x2, x3], [y2, y3]) # Recta para simplificar la visualización
        ax.plot(V_23, P_23, 'r-', linewidth=2, label='Adiabática 1 (2->3)')
        
        # Isoterma H (3 -> 4)
        ax.plot([x3, x4], [y3, y4], 'b-', linewidth=2, label='Isoterma H (3->4)')
        
        # Adiabática 2 (4 -> 1) - Cualitativa, pendiente negativa en PV
        V_41 = np.linspace(x4, x1, 50)
        P_41 = np.interp(V_41, [x4, x1], [y4, y1]) # Recta para simplificar la visualización
        ax.plot(V_41, P_41, 'r-', linewidth=2, label='Adiabática 2 (4->1)')
        
        # Puntos
        ax.plot([x1, x2, x3, x4], [y1, y2, y3, y4], 'ko', markersize=5)
        
        # Etiquetas de los puntos
        ax.text(x1 * 0.9, y1 * 0.9, point_labels[0], fontsize=12, ha='right')
        ax.text(x2 * 1.05, y2 * 0.9, point_labels[1], fontsize=12, ha='left')
        ax.text(x3 * 1.05, y3 * 1.05, point_labels[2], fontsize=12, ha='left')
        ax.text(x4 * 0.9, y4 * 1.05, point_labels[3], fontsize=12, ha='right')
        
        # Flechas de dirección
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='b', linewidth=1.5))
        ax.annotate('', xy=(x3, y3), xytext=(x2, y2),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='r', linewidth=1.5))
        ax.annotate('', xy=(x4, y4), xytext=(x3, y3),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='b', linewidth=1.5))
        ax.annotate('', xy=(x1, y1), xytext=(x4, y4),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='r', linewidth=1.5))
        
        ax.set_xlim(0.5, 5.5)
        ax.set_ylim(1.5, 4.5)
        
    # Ajuste para la pila eléctrica (E-Z)
    elif title == "(c) Pila Eléctrica (Diagrama E-Z)":
        # Eje X: Z (Carga), Eje Y: E (FEM)
        # Isoterma: E = f(T) -> E = cte a T=cte. Son líneas horizontales.
        # Adiabática: dE/dZ = pendiente positiva (dado por el problema)
        
        # Puntos cualitativos
        z1, e1 = 1.0, 2.0  # Punto 1 (TC)
        z2, e2 = 3.0, 2.0  # Punto 2 (TC) - Isoterma C
        z3, e3 = 4.0, 4.0  # Punto 3 (TH) - Isoterma H
        z4, e4 = 2.0, 4.0  # Punto 4 (TH)
        
        # Isoterma C (1 -> 2)
        ax.plot([z1, z2], [e1, e2], 'b-', linewidth=2, label='Isoterma C (1->2)')
        
        # Adiabática 1 (2 -> 3) - Pendiente positiva
        Z_23 = np.linspace(z2, z3, 50)
        E_23 = np.interp(Z_23, [z2, z3], [e2, e3])
        ax.plot(Z_23, E_23, 'r-', linewidth=2, label='Adiabática 1 (2->3)')
        
        # Isoterma H (3 -> 4)
        ax.plot([z3, z4], [e3, e4], 'b-', linewidth=2, label='Isoterma H (3->4)')
        
        # Adiabática 2 (4 -> 1) - Pendiente positiva
        Z_41 = np.linspace(z4, z1, 50)
        E_41 = np.interp(Z_41, [z4, z1], [e4, e1])
        ax.plot(Z_41, E_41, 'r-', linewidth=2, label='Adiabática 2 (4->1)')
        
        # Puntos
        ax.plot([z1, z2, z3, z4], [e1, e2, e3, e4], 'ko', markersize=5)
        
        # Etiquetas de los puntos
        ax.text(z1 * 0.9, e1 * 0.9, point_labels[0], fontsize=12, ha='right')
        ax.text(z2 * 1.05, e2 * 0.9, point_labels[1], fontsize=12, ha='left')
        ax.text(z3 * 1.05, e3 * 1.05, point_labels[2], fontsize=12, ha='left')
        ax.text(z4 * 0.9, e4 * 1.05, point_labels[3], fontsize=12, ha='right')
        
        # Flechas de dirección
        ax.annotate('', xy=(z2, e2), xytext=(z1, e1),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='b', linewidth=1.5))
        ax.annotate('', xy=(Z_23[25], E_23[25]), xytext=(Z_23[24], E_23[24]),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='r', linewidth=1.5))
        ax.annotate('', xy=(z4, e4), xytext=(z3, e3),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='b', linewidth=1.5))
        ax.annotate('', xy=(Z_41[25], E_41[25]), xytext=(Z_41[24], E_41[24]),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='r', linewidth=1.5))
        
        ax.set_xlim(0.5, 4.5)
        ax.set_ylim(1.5, 4.5)
        
    # Ajuste para la sustancia paramagnética (H-M)
    elif title == "(d) Sustancia Paramagnética (Diagrama H-M)":
        # Eje X: M (Magnetización), Eje Y: H (Campo Magnético)
        # Ley de Curie: M = C * H / T -> H = (T/C) * M. Isoterma: H es proporcional a M.
        # Adiabática: H/T = cte -> H es proporcional a T.
        # El problema dice que H/T es prácticamente constante en los procesos adiabáticos reversibles.
        # Esto implica que las adiabáticas son líneas rectas que pasan por el origen (H = cte * M).
        # La pendiente de la isoterma es T/C. La pendiente de la adiabática es H/M = cte.
        # Para un ciclo de Carnot, la isoterma H (TH) debe tener mayor pendiente que la isoterma C (TC).
        # La adiabática 1 (TC -> TH) debe ir de una pendiente menor a una mayor.
        # La adiabática 2 (TH -> TC) debe ir de una pendiente mayor a una menor.
        
        # Puntos cualitativos
        m1, h1 = 1.0, 1.0  # Punto 1 (TC)
        m2, h2 = 2.0, 2.0  # Punto 2 (TH) - Adiabática 1 (H/M = cte1)
        m3, h3 = 4.0, 4.0  # Punto 3 (TH) - Isoterma H (H = (TH/C) * M)
        m4, h4 = 2.0, 1.0  # Punto 4 (TC) - Adiabática 2 (H/M = cte2)
        
        # Isoterma C (4 -> 1) - H = (TC/C) * M. Pendiente menor.
        M_41 = np.linspace(m4, m1, 50)
        H_41 = (h1/m1) * M_41
        ax.plot(M_41, H_41, 'b-', linewidth=2, label='Isoterma C (4->1)')
        
        # Adiabática 1 (1 -> 2) - H/M = cte1. Pendiente mayor.
        M_12 = np.linspace(m1, m2, 50)
        H_12 = (h2/m2) * M_12
        ax.plot(M_12, H_12, 'r-', linewidth=2, label='Adiabática 1 (1->2)')
        
        # Isoterma H (2 -> 3) - H = (TH/C) * M. Pendiente mayor.
        M_23 = np.linspace(m2, m3, 50)
        H_23 = (h3/m3) * M_23
        ax.plot(M_23, H_23, 'b-', linewidth=2, label='Isoterma H (2->3)')
        
        # Adiabática 2 (3 -> 4) - H/M = cte2. Pendiente menor.
        M_34 = np.linspace(m3, m4, 50)
        H_34 = np.interp(M_34, [m3, m4], [h3, h4]) # Interpolar para que se vea el ciclo
        ax.plot(M_34, H_34, 'r-', linewidth=2, label='Adiabática 2 (3->4)')
        
        # Puntos
        ax.plot([m1, m2, m3, m4], [h1, h2, h3, h4], 'ko', markersize=5)
        
        # Etiquetas de los puntos
        ax.text(m1 * 0.9, h1 * 1.05, point_labels[0], fontsize=12, ha='right')
        ax.text(m2 * 1.05, h2 * 1.05, point_labels[1], fontsize=12, ha='left')
        ax.text(m3 * 1.05, h3 * 1.05, point_labels[2], fontsize=12, ha='left')
        ax.text(m4 * 0.9, h4 * 0.9, point_labels[3], fontsize=12, ha='right')
        
        # Flechas de dirección
        ax.annotate('', xy=(M_12[25], H_12[25]), xytext=(M_12[24], H_12[24]),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='r', linewidth=1.5))
        ax.annotate('', xy=(M_23[25], H_23[25]), xytext=(M_23[24], H_23[24]),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='b', linewidth=1.5))
        ax.annotate('', xy=(M_34[25], H_34[25]), xytext=(M_34[24], H_34[24]),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='r', linewidth=1.5))
        ax.annotate('', xy=(M_41[25], H_41[25]), xytext=(M_41[24], H_41[24]),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='b', linewidth=1.5))
        
        ax.set_xlim(0.5, 4.5)
        ax.set_ylim(0.5, 4.5)
        
    # Configuración común
    ax.set_xlabel(x_label, fontsize=14)
    ax.set_ylabel(y_label, fontsize=14)
    ax.set_title(title, fontsize=16)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right')
    ax.set_aspect('auto') # Asegura que el aspecto sea auto para que no se distorsione

    # Invertir ejes si es necesario
    if reverse_x:
        ax.invert_xaxis()
    if reverse_y:
        ax.invert_yaxis()

# --- Funciones de curva para el Gas Ideal (a) ---
# P = nRT/V (Isoterma) -> P = cte/V
def isotherm_ideal_gas(V, V_start, P_start, V_end, P_end):
    # Usamos la relación P*V = cte
    cte = P_start * V_start
    return cte / V

# P * V^gamma = cte (Adiabática) -> P = cte / V^gamma
# Usaremos un gamma cualitativo (e.g., 1.4)
def adiabatic_ideal_gas(V, V_start, P_start, V_end, P_end, gamma=1.4):
    # Ajustamos la constante para que pase por el punto inicial
    cte = P_start * (V_start ** gamma)
    return cte / (V ** gamma)

# --- Creación de los gráficos ---

fig, axs = plt.subplots(2, 2, figsize=(14, 12))
axs = axs.flatten()

# (a) Gas Ideal (Diagrama P-V)
draw_carnot_cycle(
    ax=axs[0],
    x_label='Volumen, V',
    y_label='Presión, P',
    title='(a) Gas Ideal (Diagrama P-V)',
    x_range=[1.0, 3.0],
    y_range=[1.0, 5.0],
    isotherm_func_H=lambda V, vs, ps, ve, pe: isotherm_ideal_gas(V, vs, ps, ve, pe),
    isotherm_func_C=lambda V, vs, ps, ve, pe: isotherm_ideal_gas(V, vs, ps, ve, pe),
    adiabatic_func_1=lambda V, vs, ps, ve, pe: adiabatic_ideal_gas(V, vs, ps, ve, pe),
    adiabatic_func_2=lambda V, vs, ps, ve, pe: adiabatic_ideal_gas(V, vs, ps, ve, pe),
    point_labels=['1', '2', '3', '4']
)

# (b) Líquido en equilibrio con su vapor (Diagrama P-V)
# Las funciones de curva no se usan en este caso, se dibuja por segmentos rectos
draw_carnot_cycle(
    ax=axs[1],
    x_label='Volumen, V',
    y_label='Presión, P',
    title='(b) Líquido-Vapor (Diagrama P-V)',
    x_range=[1.0, 5.0],
    y_range=[2.0, 4.0],
    isotherm_func_H=None,
    isotherm_func_C=None,
    adiabatic_func_1=None,
    adiabatic_func_2=None,
    point_labels=['A', 'B', 'C', 'D'] # Usar otras etiquetas para diferenciar
)

# (c) Pila eléctrica reversible (Diagrama E-Z)
# Las funciones de curva no se usan en este caso, se dibuja por segmentos rectos
draw_carnot_cycle(
    ax=axs[2],
    x_label='Carga, Z',
    y_label='Fuerza Electromotriz, E',
    title='(c) Pila Eléctrica (Diagrama E-Z)',
    x_range=[1.0, 4.0],
    y_range=[2.0, 4.0],
    isotherm_func_H=None,
    isotherm_func_C=None,
    adiabatic_func_1=None,
    adiabatic_func_2=None,
    point_labels=['1', '2', '3', '4']
)

# (d) Sustancia paramagnética (Diagrama H-M)
# Las funciones de curva no se usan en este caso, se dibuja por segmentos rectos
draw_carnot_cycle(
    ax=axs[3],
    x_label='Magnetización, M',
    y_label='Campo Magnético, H',
    title='(d) Sustancia Paramagnética (Diagrama H-M)',
    x_range=[1.0, 4.0],
    y_range=[1.0, 4.0],
    isotherm_func_H=None,
    isotherm_func_C=None,
    adiabatic_func_1=None,
    adiabatic_func_2=None,
    point_labels=['1', '2', '3', '4']
)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "carnot_cycles_all.png"))
plt.close(fig)

print(f"Diagramas guardados en {output_dir}/carnot_cycles_all.png")