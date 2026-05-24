import serial
import time
esp = serial.Serial('COM3', 115200) #puerto y velocidad de comunicación
time.sleep(2) #tiempo de espera para establecer la comunicación 
print("COMUNICACIÓN SERIAL INICIADA") #mensaje de inicio de comunicación
print("ENCENDIENDO EL LED...") #mensaje de encendido del LED
esp.write(b'1') #envía el byte '1' al ESP-32 para encender el LED
time.sleep(5) #espera 5 segundos
print("APAGANDO EL LED...") #mensaje de apagado del LED
esp.write(b'0') #envía el byte '0' al ESP-32 para apagar el LED
time.sleep(5) #espera 5 segundos    
esp.close() #cierra la comunicación serial
print("COMUNICACIÓN SERIAL FINALIZADA") #mensaje de finalización de comunicación
