import paho.mqtt.client as mqtt
import requests
import json
import sys
import time # Importante para calcular los 60 segundos

# CONFIGURACIÓN DEL ENTORNO SMAT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "fisi/smat/estaciones/+/lecturas"

API_URL = "http://localhost:8000/lecturas/"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJKZWljayIsImV4cCI6MTc4MTExMDgxMH0.TMYj8i6AtVcLONOJ4994cONSM0mA-nDz50l_Y5eOZSc" 

estado_estaciones = {}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("🟢 Conectado exitosamente al Broker MQTT")
        # Suscribirse al tópico global de lecturas de estaciones
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Escuchando transmisiones en el tópico: {MQTT_TOPIC}")
    else:
        print(f"🔴 Error de conexión al Broker. Código de retorno: {rc}")
        sys.exit(1)


def on_message(client, userdata, msg):
    try:
        payload_raw = msg.payload.decode("utf-8")
        data_json = json.loads(payload_raw)
        
        topic_parts = msg.topic.split('/')
        estacion_id = int(topic_parts[3])
        valor_actual = float(data_json["valor"])
        tiempo_actual = time.time()
        
        print(f"📩 Telemetría recibida de Estación [{estacion_id}]: {data_json}")

        enviar_a_api = False
        razon_envio = ""

        if estacion_id not in estado_estaciones:
            enviar_a_api = True
            razon_envio = "Primera lectura detectada"
        else:
            ultimo_valor = estado_estaciones[estacion_id]["ultimo_valor"]
            ultimo_tiempo = estado_estaciones[estacion_id]["ultimo_tiempo"]
            
            if ultimo_valor != 0:
                variacion = abs(valor_actual - ultimo_valor) / abs(ultimo_valor)
            else:
                variacion = 1.0
            
            tiempo_transcurrido = tiempo_actual - ultimo_tiempo

            if variacion > 0.05:
                enviar_a_api = True
                razon_envio = f"Variación significativa ({(variacion*100):.2f}% > 5%)"
            elif tiempo_transcurrido > 60:
                enviar_a_api = True
                razon_envio = f"Reporte de vida (Pasaron {tiempo_transcurrido:.1f}s > 60s)"
        

        if enviar_a_api:
            api_payload = {
                "valor": valor_actual,
                "estacion_id": estacion_id
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {JWT_TOKEN}"
            }
            
            response = requests.post(API_URL, json=api_payload, headers=headers)

            if response.status_code in [200, 201]:
                print(f"💾 [DB Sincronizada] Lectura de {api_payload['valor']} cm guardada. Razón: {razon_envio}")
                estado_estaciones[estacion_id] = {
                    "ultimo_valor": valor_actual,
                    "ultimo_tiempo": tiempo_actual
                }
            else:
                print(f"⚠️ [Fallo de Ingesta] API rechazó el dato. Código: {response.status_code} - {response.text}")
        else:
            print(f"🛡️ [Filtro Activo] Lectura ignorada para Estación [{estacion_id}]: {valor_actual} cm (Redundante).")

    except KeyError as e:
        print(f"❌ Error de esquema: Falta la llave {e} en el payload MQTT.")
    except ValueError:
        print("❌ Error de casteo: El valor o el ID de la estación no son numéricos.")
    except Exception as e:
        print(f"❌ Error crítico en el Bridge: {e}")

# Inicialización del cliente de red MQTT
bridge_client = mqtt.Client()
bridge_client.on_connect = on_connect
bridge_client.on_message = on_message

try:
    print("🚀 Inicializando el Bridge de Acoplamiento SMAT con Filtro Anti-Ruido...")
    bridge_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    # Mantener el hilo escuchando activamente de forma síncrona
    bridge_client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 Bridge detenido por el administrador.")