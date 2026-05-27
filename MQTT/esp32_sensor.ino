// Pines del ESP32
int led   = 26;
int fotor = 33;
int t = 5000;

int  fotoval = 0;
int estadoLED = 0;
char comando;

// Temporizador
unsigned long ultimaLectura = 0;
const unsigned long intervalo = 3000; // 3 segundos

void setup() {
    pinMode(led, OUTPUT);
    Serial.begin(115200);
    delay(t);
}

void loop() {
    // Revisar comando serial SIEMPRE, sin bloquear 
    if (Serial.available() > 0) {
        comando = Serial.read(); // ← corregido: leer en 'comando', no en 'var'


if (comando == '1') {
      digitalWrite(led, HIGH); 
      estadoLED = 1;
    } else if (comando == '0') {
      digitalWrite(led, LOW);   
      estadoLED = 0;
    }
    // Cualquier otro byte es ignorado silenciosamente
  }

 // 2. Leer y enviar datos cada 3 segundos usando millis
    if (millis() - ultimaLectura >= intervalo) {
        ultimaLectura = millis();

        fotoval = analogRead(fotor); // ← una sola lectura dentro del bloque

        Serial.print("val fotore:");
        Serial.print(fotoval);
        Serial.print(",LED:");
        Serial.println(estadoLED);
    }
}