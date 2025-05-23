#include <WiFi.h>
#include <HTTPClient.h>

// Tu red WiFi
const char* ssid = "Alumnes";
const char* password = "edu71243080";

// URL de Flask
const char* servidorFlask = "http://172.16.1.194:81/esp32"; 
const int botonSI = 22;
const int botonNO = 23;

bool estadoAnteriorSI = HIGH;
bool estadoAnteriorNO = HIGH;

void setup() {
  Serial.begin(115200);

  pinMode(botonSI, INPUT);
  pinMode(botonNO, INPUT);

  // Conexión WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado. IP: " + WiFi.localIP().toString());
}

void loop() {
  bool estadoActualSI = digitalRead(botonSI);
  bool estadoActualNO = digitalRead(botonNO);

  if (estadoAnteriorSI == LOW && estadoActualSI == HIGH) {
    Serial.println("SI pulsado → enviando true");
    enviarDato(true);
  }

  if (estadoAnteriorNO == LOW && estadoActualNO == HIGH) {
    Serial.println("NO pulsado → enviando false");
    enviarDato(false);
  }

  estadoAnteriorSI = estadoActualSI;
  estadoAnteriorNO = estadoActualNO;

  delay(20);
}

void enviarDato(bool valor) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(servidorFlask); // Ya incluye /esp32
    http.addHeader("Content-Type", "application/json");

    String body = "{\"valor\": " + String(valor ? "true" : "false") + "}";
    int codigo = http.POST(body);

    if (codigo > 0) {
      String respuesta = http.getString();
      Serial.println("Enviado correctamente: " + body);
      Serial.println("Respuesta: " + respuesta);
    } else {
      Serial.println("Error al enviar: " + String(http.errorToString(codigo).c_str()));
    }

    http.end();
  } else {
    Serial.println("WiFi desconectado");
  }
}
