from app.mqtt_client import run_mqtt_client
from app import app
import threading


if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=run_mqtt_client)
    mqtt_thread.start()
    app.run_server(debug=True, host='0.0.0.0', port=5000)  # Use run_server for Dash
