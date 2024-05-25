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
TOPICS = {
    "ttndata": "ttndata",
    "senzory": "Senzory - wifi",
    "mve": "mve",
    "Bilina": "Bílina - kamery",
    "vodomery": "Děčín - vodoměry",
    "udp1881": "UDP 1881",
    "unknown": "Neznámé",
}

mqtt_data = {value: [] for value in TOPICS.keys()}


def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    json_size = get_msg_size(msg)
    if json_size == -1:
        return

    topic = msg.topic.strip("/").split("/")[0]

    if topic in TOPICS.keys():
        mqtt_data[topic].append(
            {
                "topic": msg.topic,
                "topic_readable": TOPICS[topic],
                "size": json_size,
                "timestamp": datetime.datetime.now(),
            }
        )
    else:
        mqtt_data["unknown"].append(
            {
                "topic": msg.topic,
                "topic_readable": TOPICS["unknown"],
                "size": json_size,
                "timestamp": datetime.datetime.now(),
            }
        )


def run_mqtt_client():
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
    mqttc.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect(MQTT_BROKER, 8883, 60)
    mqttc.loop_forever()


def get_msg_size(msg):
    try:
        payload = msg.payload.decode("utf-8")
    except UnicodeDecodeError:
        print("Failed to decode payload with UTF-8")
        return -1

    try:
        json_payload = json.loads(msg.payload)
        json_bytes = json.dumps(json_payload).encode("utf-8")
        return len(json_bytes)
    except json.JSONDecodeError:
        print("Payload is not in JSON format")
        return -1
