import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button
from scipy.integrate import quad

# ─────────────────────────────────────────────
#  PARÁMETROS FÍSICOS E INICIALES
# ─────────────────────────────────────────────
l   = 1.0    # Longitud de la cuerda
c0  = 1.0    # Velocidad de propagación
N   = 5     # Número de armónicos
b   = 0.25   # Parámetro de base del triángulo  (0 < b < 0.5)
h   = 0.50   # Altura del triángulo
dt  = 0.025  # Paso de tiempo por fotograma

# ─────────────────────────────────────────────
#  CONDICIÓN INICIAL  f(x)  —  triangular
#
#        h
#       /\      /\
#      /  \    /  \
#  0  /    \  /    \  0
#    0   b  \/  1-b  1
#
#  f(x) = (h/b)·x                          , 0   ≤ x ≤ b
#  f(x) = h - 2h/(1-2b)·(x-b)             , b   ≤ x ≤ 1-b
#  f(x) = (h/b)·(x-1)                     , 1-b ≤ x ≤ 1
# ─────────────────────────────────────────────
def f_inicial(x, b, h, l=1.0):
    """Condición inicial triangular a trozos."""
    x = np.asarray(x, dtype=float)
    u = np.zeros_like(x)
    r1 = x <= b # (equivale a x <= b para l=1)
    r2 = (x > b) & (x <= l - b) # (equivale a b < x <= 1-b para l=1)
    r3 = x > l - b # (equivale a x >= 1-b para l=1)
    u[r1] = (h / b) * x[r1] # Triángulo creciente
    u[r2] = h - (2*h / (l - 2*b)) * (x[r2] - b) # Triángulo decreciente
    u[r3] = (h / b) * (x[r3] - l) # Triángulo creciente (negativo)
    return u

# ─────────────────────────────────────────────
#  COEFICIENTES DE FOURIER  a_k
#  u_t(x,0) = 0  →  solo cosenos en t
# ─────────────────────────────────────────────
def calcular_coeficientes(N, b, h, l):
    integrando = lambda x, k: f_inicial(x, b, h, l) * np.sin(k * np.pi * x / l)
    a = np.zeros(N)
    for k in range(1, N + 1):
        integral, _ = quad(integrando, 0, l, args=(k,), limit=200)
        a[k - 1] = (2.0 / l) * integral
    return a

a = calcular_coeficientes(N, b, h, l)

# ─────────────────────────────────────────────
#  FUNCIÓN  u(x, t)
# ─────────────────────────────────────────────
def calcular_u(x, t, a, c, l):
    k = np.arange(1, len(a) + 1)
    espacial = np.sin(k[None, :] * np.pi * x[:, None] / l)
    temporal = np.cos(k[None, :] * np.pi * c * t    / l)
    return (a[None, :] * espacial * temporal).sum(axis=1)

# ─────────────────────────────────────────────
#  FIGURA Y EJES
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
plt.subplots_adjust(left=0.1, right=0.97, bottom=0.42, top=0.92)

ax.set_xlim(0, l)
ax.set_ylim(-1.5, 1.5)
ax.set_title("Cuerda vibrante — condición inicial triangular", fontsize=13)
ax.set_xlabel("Posición x")
ax.set_ylabel("Amplitud u(x, t)")
ax.grid(True, alpha=0.35)

x_pts     = np.linspace(0, l, 400)
(linea,)  = ax.plot([], [], lw=2.2, color="#534AB7", label="u(x, t)")
(linea_f,)= ax.plot(x_pts, f_inicial(x_pts, b, h, l),
                    lw=1.4, ls="--", color="#D85A30", alpha=0.55, label="f(x) inicial")
tiempo_txt = ax.text(0.02, 1.35, "t = 0.000", fontsize=10, color="#888")
ax.legend(loc="upper right", fontsize=9)

# ─────────────────────────────────────────────
#  SLIDERS
# ─────────────────────────────────────────────
ax_b     = plt.axes([0.15, 0.32, 0.65, 0.025])
ax_h     = plt.axes([0.15, 0.27, 0.65, 0.025])
ax_n     = plt.axes([0.15, 0.22, 0.65, 0.025])
ax_c     = plt.axes([0.15, 0.17, 0.65, 0.025])
ax_speed = plt.axes([0.15, 0.12, 0.65, 0.025])
ax_play  = plt.axes([0.15, 0.03, 0.18, 0.055])
ax_reset = plt.axes([0.37, 0.03, 0.18, 0.055])
ax_showf = plt.axes([0.59, 0.03, 0.18, 0.055])

sl_b     = Slider(ax_b,     "b (base)",        0.05, 0.45, valinit=b,   valstep=0.01)
sl_h     = Slider(ax_h,     "h (altura)",      0.05, 1.20, valinit=h,   valstep=0.05)
sl_n     = Slider(ax_n,     "Armónicos N",     1,    80,   valinit=N,   valstep=1)
sl_c     = Slider(ax_c,     "Velocidad c",     0.2,  3.0,  valinit=c0,  valstep=0.1)
sl_speed = Slider(ax_speed, "Vel. animación",  0.005, 0.1, valinit=dt,  valstep=0.005)

btn_play  = Button(ax_play,  "Pausar",    color="#e8e6f8")
btn_reset = Button(ax_reset, "Reiniciar", color="#e8e6f8")
btn_showf = Button(ax_showf, "Ocultar f(x)", color="#fde8dc")

# ─────────────────────────────────────────────
#  ESTADO MUTABLE
# ─────────────────────────────────────────────
estado = {
    "t": 0.0, "running": True,
    "a": a.copy(), "c": c0, "dt": dt,
    "b": b, "h": h,
}

# ─────────────────────────────────────────────
#  CALLBACKS
# ─────────────────────────────────────────────
def recalcular(val=None):
    nuevo_b = sl_b.val
    nuevo_h = sl_h.val
    nuevo_N = int(sl_n.val)
    estado["b"] = nuevo_b
    estado["h"] = nuevo_h
    estado["a"] = calcular_coeficientes(nuevo_N, nuevo_b, nuevo_h, l)
    linea_f.set_ydata(f_inicial(x_pts, nuevo_b, nuevo_h, l))
    fig.canvas.draw_idle()

sl_b.on_changed(recalcular)
sl_h.on_changed(recalcular)
sl_n.on_changed(recalcular)

sl_c.on_changed(lambda val: estado.update({"c": val}))
sl_speed.on_changed(lambda val: estado.update({"dt": val}))

def on_play(event):
    estado["running"] = not estado["running"]
    btn_play.label.set_text("Reanudar" if not estado["running"] else "Pausar")

def on_reset(event):
    estado["t"] = 0.0

def on_showf(event):
    vis = not linea_f.get_visible()
    linea_f.set_visible(vis)
    btn_showf.label.set_text("Ocultar f(x)" if vis else "Mostrar f(x)")

btn_play.on_clicked(on_play)
btn_reset.on_clicked(on_reset)
btn_showf.on_clicked(on_showf)

# ─────────────────────────────────────────────
#  ANIMACIÓN
# ─────────────────────────────────────────────
def inicializar():
    linea.set_data([], [])
    return (linea,)

def animar(frame):
    if estado["running"]:
        estado["t"] += estado["dt"]
    u = calcular_u(x_pts, estado["t"], estado["a"], estado["c"], l)
    linea.set_data(x_pts, u)
    tiempo_txt.set_text(f"t = {estado['t']:.3f}")
    return (linea, tiempo_txt)

ani = animation.FuncAnimation(
    fig, animar,
    init_func=inicializar,
    frames=None,
    interval=30,
    blit=True,
    cache_frame_data=False,
)

plt.show()