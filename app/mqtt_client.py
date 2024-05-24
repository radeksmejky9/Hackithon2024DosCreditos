import datetime
import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import json
import ssl

load_dotenv()
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
mqtt_data = []


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        try:
            json_payload = json.loads(payload)
            json_bytes = json.dumps(json_payload).encode("utf-8")
            json_size = len(json_bytes)
            print(f"{msg.topic} - JSON payload size: {json_size} bytes")

            mqtt_data.append(
                {
                    "topic": msg.topic,
                    "size": json_size,
                    "timestamp": datetime.datetime.now(),
                }
            )
        except json.JSONDecodeError:
            print("Payload is not in JSON format")
    except UnicodeDecodeError:
        print("Failed to decode payload with UTF-8")


def run_mqtt_client():
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
    mqttc.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect(MQTT_BROKER, 8883, 60)
    mqttc.loop_forever()
