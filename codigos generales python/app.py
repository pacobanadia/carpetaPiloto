from flask import Flask, request, jsonify, render_template_string
import random
import threading # Para manejar la simulación en segundo plano
import time # Para pausas en la simulación

app = Flask(__name__)

# Estructura para almacenar los datos del sensor
# Usamos un diccionario para que sea fácil de actualizar y acceder
sensor_data = {
    'real_temperature': 'N/A',
    'real_humidity': 'N/A'
}

# Estructura para los datos simulados
simulated_data = {
    'sim_temperature': 0,
    'sim_humidity': 0
}

# --- Simulación de datos en segundo plano ---
def simulate_data():
    """
    Esta función se ejecuta en un hilo separado para generar 
    datos de temperatura y humedad al azar continuamente.
    """
    while True:
        # Genera valores aleatorios con un rango lógico
        simulated_data['sim_temperature'] = round(random.uniform(15.0, 30.0), 2)
        simulated_data['sim_humidity'] = round(random.uniform(30.0, 70.0), 2)
        # Espera 2 segundos, igual que el Arduino
        time.sleep(2)

# --- Rutas de la aplicación web ---

@app.route('/')
def index():
    """
    Página principal que muestra los datos.
    Utiliza render_template_string para mantener todo en un solo archivo.
    """
    # Plantilla HTML con estilos básicos para mostrar los datos
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard de Sensores</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
            h1 { color: #333; }
            .container { display: flex; justify-content: space-around; }
            .card { background-color: white; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1 ); padding: 20px; margin: 10px; width: 40%; }
            .card h2 { color: #555; border-bottom: 2px solid #eee; padding-bottom: 10px; }
            p { font-size: 24px; color: #007BFF; text-align: center; }
            .label { font-size: 16px; color: #666; }
        </style>
    </head>
    <body>
        <h1>Dashboard de Monitoreo de Temperatura y Humedad</h1>
        <div class="container">
            <div class="card">
                <h2>Sensor Real (ESP-32)</h2>
                <p><span class="label">Temperatura:</span> {{ real_temp }} °C</p>
                <p><span class="label">Humedad:</span> {{ real_hum }} %</p>
            </div>
            <div class="card">
                <h2>Sensor Simulado</h2>
                <p><span class="label">Temperatura:</span> {{ sim_temp }} °C</p>
                <p><span class="label">Humedad:</span> {{ sim_hum }} %</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html_template,
        real_temp=sensor_data['real_temperature'], # Datos reales del ESP-32
        real_hum=sensor_data['real_humidity'], # Datos reales del ESP-32    
        sim_temp=simulated_data['sim_temperature'], # Datos simulados
        sim_hum=simulated_data['sim_humidity'] # Datos simulados
    )

@app.route('/data', methods=['POST'])  # Endpoint para recibir datos del ESP-32
def receive_data():
    """
    Endpoint para recibir los datos del ESP-32.
    Espera un JSON con 'temperatura' y 'humedad'.
    """
    if request.is_json: # Verificamos que el contenido sea JSON
        data = request.get_json()
        # Actualizamos los valores globales de forma segura
        sensor_data['real_temperature'] = data.get('temperatura', 'N/A')
        sensor_data['real_humidity'] = data.get('humedad', 'N/A')
        print(f"Datos recibidos: Temp={sensor_data['real_temperature']}°C, Humedad={sensor_data['real_humidity']}%")
        return jsonify({"status": "success", "message": "Datos recibidos"}), 200
    else:
        return jsonify({"status": "error", "message": "El formato no es JSON"}), 400

if __name__ == '__main__':
    # Iniciar el hilo para la simulación de datos
    simulation_thread = threading.Thread(target=simulate_data, daemon=True)
    simulation_thread.start()
    
    # Iniciar el servidor Flask
    # host='0.0.0.0' permite que sea accesible desde otros dispositivos en la misma red
    app.run(host='0.0.0.0', port=5000, debug=True)
    