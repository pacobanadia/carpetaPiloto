"""SUSCRIPCIÓN MQTT ENTRE ESP-32 Y PYTHON"""
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Conectado con código de resultado: " + str(rc))
    client.subscribe("led/control") #suscripción al TOPICO led/control
def on_message(client, userdata, msg):
    print("Mensaje recibido: " + msg.topic + " " + str(msg.payload.decode())) #imprime el mensaje recibido, VALOR, TEXTO O JSON

client = mqtt.Client() #crea una instancia del cliente MQTT
client.on_connect = on_connect #asigna la función de conexión al evento de conexión
client.on_message = on_message #asigna la función de mensaje al evento de mensaje

client.connect("broker.hivemq.com", 1883, 60) #conecta al broker MQTT, HiveMQ, PUERTO, TIEMPO DE ESPERA
client.loop_forever() #mantiene el cliente en ejecución para recibir mensajes