import paho.mqtt.client as mqtt

# Define MQTT broker and topic information
broker_address = "192.168.1.86"
broker_port = 1883
status_topic = "$SYS/broker/connection/+/state"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe(status_topic)
    else:
        print(f"Failed to connect, error code: {rc}")

def on_message(client, userdata, message):
    if message.topic.startswith("$SYS/broker/connection/"):
        client_id = message.topic.split("/")[-2]
        print(f"Device connected: {client_id}")

# Create MQTT client instance for monitoring
monitoring_client = mqtt.Client()

# Set the callback functions
monitoring_client.on_connect = on_connect
monitoring_client.on_message = on_message

# Connect to the MQTT broker
monitoring_client.connect(broker_address, broker_port, 60)

# Start the MQTT loop to process incoming messages
monitoring_client.loop_start()

# Keep the client running and receiving messages (use client.loop_forever() if you don't have additional code)
while True:
    pass
