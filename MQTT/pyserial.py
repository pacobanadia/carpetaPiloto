"""COMUNICACIÓN SERIAL ENTRE ESP-32 Y PYTHON"""
import serial
import time 
esp = serial.Serial('COM3', 115200) #puerto y velocidad de comunicación
time.sleep(2) #tiempo de espera para establecer la comunicación
print("COMUNICACIÓN SERIAL INICIADA") #mensaje de inicio de comunicación
while True:
    if esp.in_waiting > 0: #si hay datos disponibles para leer
        data = esp.readline().decode('utf-8').rstrip() #lee la línea de datos y decodifica
        print("Los datos recibidos: ", data) #imprime los datos recibidos
        if data == '1': #si el dato recibido es '1'
            print('LED ENCENDIDO') #imprime mensaje de LED encendido
        elif data == '0': #si el dato recibido es '0'
            print('LED APAGADO') #imprime mensaje de LED apagado
        else:
            print('DATO DESCONOCIDO') #imprime mensaje de dato desconocido
