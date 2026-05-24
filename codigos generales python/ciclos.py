nota = float(input("Digite la nota del alumno: "))

if nota < 3.0:
    print("Reprobado")
elif 3.0 <= nota < 3.8:
    print("Aprobado")
elif 3.8 <= nota < 4.5:
    print("Notable")
elif 4.5 <= nota <= 5.0:
    print("Sobresaliente")
else:
    print("Nota inválida")      