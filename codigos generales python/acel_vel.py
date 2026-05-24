# Lista de aceleraciones
a = [2.5, 1.8, 3.2, 2.1, 1.5]

# Velocidad inicial
v0 = 10.0

# Crear lista de velocidades usando ciclo for
velocidades = []
i = 0

# Usar while para iterar sobre las aceleraciones
while i <= len(a):
    # Calcular v[i] = v0 + suma de aceleraciones hasta i-1
    suma_aceleraciones = 0
    
    # Usar for para sumar las aceleraciones
    for k in range(i):
        suma_aceleraciones += a[k]
    
    # Calcular velocidad en el instante i
    v_i = v0 + suma_aceleraciones
    velocidades.append(v_i)
    
    i += 1

# Mostrar todas las velocidades
print("Lista de velocidades:")
for i in range(len(velocidades)):
    print(f"v[{i}] = {velocidades[i]:.2f}")

# Encontrar la velocidad máxima usando while
velocidad_maxima = velocidades[0]
j = 1

while j < len(velocidades):
    if velocidades[j] > velocidad_maxima:
        velocidad_maxima = velocidades[j]
    j += 1

print(f"\nLa velocidad máxima es: {velocidad_maxima:.2f}")
print(f"Posición en la lista: {velocidades.index(velocidad_maxima)}")