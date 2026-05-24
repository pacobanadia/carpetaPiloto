"""PUBLICACIÓN MQTT ENTRE ESP-32 Y PYTHON"""
import paho.mqtt.client as mqtt

client = mqtt.Client()  
#crea una instancia del cliente MQTT
client.connect("broker.hivemq.com", 1883, 60) #conecta al broker MQTT, HiveMQ, PUERTO, TIEMPO DE ESPERA
client.publish("led/control", "1") #publica el mensaje '1' en el TOPICO led/control para encender el LED
print("Mensaje '1' publicado en el TOPICO led/control para encender el LED")
client.publish("led/control", "0") #publica el mensaje '0' en el TOPICO led/control para apagar el LED
print("Mensaje '0' publicado en el TOPICO led/control para apagar el LED")
