"""
Animación de cuerda pulsada — solución de la ecuación de onda

    u(x, t) = (2*v0)/(pi*c) * sum_{n=1}^{N} (1/n)
              * sin(n*pi*b/l) * sin(n*pi*c*t/l) * sin(n*pi*x/l)

Parámetros ajustables al inicio del script.
Dependencias: numpy, matplotlib
    pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button

# ── Parámetros físicos ─────────────────────────────────────────────────────────
L   = 1.0        # longitud de la cuerda (m)
c   = 1.0        # velocidad de onda (m/s)
v0  = 1.0        # magnitud de la velocidad inicial en b
b   = 0.3        # posición de la pulsación (fracción de L)
N   = 60         # número de términos de la serie de Fourier
# ──────────────────────────────────────────────────────────────────────────────

# Malla espacial
Nx   = 500
x    = np.linspace(0, L, Nx)

# Precalcular coeficientes independientes del tiempo
ns   = np.arange(1, N + 1)                        # (N,)
An   = (2 * v0) / (np.pi * c)
coef = An * (1 / ns) * np.sin(ns * np.pi * b / L) # (N,)

# Precalcular sin(n*pi*x/L) para toda la malla → (N, Nx)
sin_x = np.sin(np.outer(ns * np.pi / L, x))       # (N, Nx)

def u_at(t: float) -> np.ndarray:
    """Desplazamiento u(x, t) vectorizado."""
    sin_t = np.sin(ns * np.pi * c * t / L)        # (N,)
    return (coef * sin_t) @ sin_x                  # (Nx,)

# ── Figura ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 4.5))
plt.subplots_adjust(left=0.08, right=0.97, bottom=0.28, top=0.93)

ax.set_xlim(0, L)
ax.set_ylim(-0.7, 0.7)
ax.set_xlabel("x / l", fontsize=11)
ax.set_ylabel("u(x, t)", fontsize=11)
ax.set_title("Cuerda pulsada — solución de la ecuación de onda", fontsize=12)
ax.axhline(0, color="gray", lw=0.6, ls="--")
ax.axvline(b * L, color="#888", lw=0.8, ls=":", label=f"posición b = {b:.2f}l")
ax.legend(fontsize=9, loc="upper right")

(line,)  = ax.plot([], [], lw=2, color="#534AB7")
dot_b,   = ax.plot([], [], "o", color="#D85A30", ms=7, zorder=5)
time_txt = ax.text(0.02, 0.92, "", transform=ax.transAxes, fontsize=10)

# ── Sliders ────────────────────────────────────────────────────────────────────
ax_b   = plt.axes([0.12, 0.17, 0.55, 0.03])
ax_N   = plt.axes([0.12, 0.11, 0.55, 0.03])
ax_spd = plt.axes([0.12, 0.05, 0.55, 0.03])

sl_b   = Slider(ax_b,   "b / l",   0.05, 0.95, valinit=b,    valstep=0.01,  color="#534AB7")
sl_N   = Slider(ax_N,   "N terms", 1,    120,   valinit=N,    valstep=1,     color="#534AB7")
sl_spd = Slider(ax_spd, "speed",   0.1,  4.0,   valinit=1.0, valstep=0.05,  color="#534AB7")

# Botón pausa/reanudar
ax_btn  = plt.axes([0.78, 0.08, 0.12, 0.07])
btn     = Button(ax_btn, "Pause", color="#e8e6f5", hovercolor="#c8c4e8")

# ── Estado de la animación ─────────────────────────────────────────────────────
state = {"t": 0.0, "running": True, "dt_real": 0.0}

# Precálculo mutable (se regenera al mover sliders)
cache = {"ns": ns, "coef": coef, "sin_x": sin_x, "b": b * L}

def rebuild_cache(b_frac, n_terms):
    ns_  = np.arange(1, int(n_terms) + 1)
    coef_= An * (1 / ns_) * np.sin(ns_ * np.pi * b_frac / L)
    sx_  = np.sin(np.outer(ns_ * np.pi / L, x))
    cache["ns"]    = ns_
    cache["coef"]  = coef_
    cache["sin_x"] = sx_
    cache["b"]     = b_frac * L
    ax.lines[-1].set_xdata([b_frac * L, b_frac * L])   # barra vertical

def compute(t):
    sin_t = np.sin(cache["ns"] * np.pi * c * t / L)
    return (cache["coef"] * sin_t) @ cache["sin_x"]

# ── Callbacks sliders ──────────────────────────────────────────────────────────
def on_slider(val):
    rebuild_cache(sl_b.val, sl_N.val)

sl_b.on_changed(on_slider)
sl_N.on_changed(on_slider)

def toggle(event):
    state["running"] = not state["running"]
    btn.label.set_text("Resume" if not state["running"] else "Pause")

btn.on_clicked(toggle)

# ── Animación ─────────────────────────────────────────────────────────────────
FPS      = 60
interval = 1000 // FPS   # ms entre frames

def init():
    line.set_data([], [])
    dot_b.set_data([], [])
    time_txt.set_text("")
    return line, dot_b, time_txt

def animate(frame):
    if state["running"]:
        # dt real según FPS y multiplicador de velocidad
        state["t"] += (interval / 1000) * sl_spd.val

    t = state["t"]
    y = compute(t)

    line.set_data(x, y)
    bx = cache["b"]
    by = compute(t)[int(bx / L * (Nx - 1))]
    dot_b.set_data([bx], [by])
    time_txt.set_text(f"t = {t:.3f} s")
    return line, dot_b, time_txt

ani = animation.FuncAnimation(
    fig, animate,
    init_func=init,
    interval=interval,
    blit=True,
    cache_frame_data=False,
)

plt.show()

