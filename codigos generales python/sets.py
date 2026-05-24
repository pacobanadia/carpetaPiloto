conjunto = set([2, 3, 4, 5])
conjunto_1=set([ 2, 3, 4])
conjunto.add(1)  # --- IGNORE ---
print(conjunto_1.issubset(conjunto))
print(conjunto.intersection(conjunto_1))
