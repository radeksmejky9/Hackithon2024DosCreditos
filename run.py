from app.mqtt_client import run_mqtt_client
from app import app
import threading

if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=run_mqtt_client)
    mqtt_thread.start()
    app.run()
