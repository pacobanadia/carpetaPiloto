def suma( num_1= 3, num_2 = 5):
    return num_1 + num_2    
print(suma(2,num_2=4))
print(suma(num_1=7, num_2=7))


variable = 3
def funcion():
    global variable 
    variable = 5
funcion()
print(variable)