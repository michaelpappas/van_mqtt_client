import logging
import signal
import sys
import json
from time import sleep
import paho.mqtt.client as mqtt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from models import Water, Battery

load_dotenv()
# Configure the PostgreSQL connection
db_user = 'mpappas'
db_password = os.environ['db_password']
# db_password = 'postgres'
db_host = 'localhost'
db_port = '5432'
db_name = 'van_data'

TANK_CAPACITY = 21

db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Congifure db connection
db = create_engine(db_url)

Session = sessionmaker(db)
session = Session()


# Initialize Logging
logging.basicConfig(level=logging.WARNING)  # Global logging configuration
logger = logging.getLogger("main")  # Logger for this module
logger.setLevel(logging.INFO) # Debugging for this file.



# Global Variables
BROKER_HOST = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "pi"
client = None  # MQTT client instance. See init_mqtt()
ALL_TOPICS = "#"
WATER_CAP = 21 # Total water tank capacity in gallons

"""
MQTT Related Functions and Callbacks
"""
def on_connect(client, user_data, flags, connection_result_code):
    """on_connect is called when our program connects to the MQTT Broker.
       Always subscribe to topics in an on_connect() callback.
       This way if a connection is lost, the automatic
       re-connection will also results in the re-subscription occurring."""

    if connection_result_code == 0:
        # 0 = successful connection
        logger.info("Connected to MQTT Broker")
    else:
        # connack_string() gives us a user friendly string for a connection code.
        logger.error("Failed to connect to MQTT Broker: " + mqtt.connack_string(connection_result_code))

    # Subscribe to the topic for LED level changes.
    client.subscribe(ALL_TOPICS, qos=2)



def on_disconnect(client, user_data, disconnection_result_code):
    """Called disconnects from MQTT Broker."""
    logger.error("Disconnected from MQTT Broker")



def on_message(client, userdata, msg):
    """Callback called when a message is received on a subscribed topic
       message topic is split and various function are called depending on the first
       topic called."""
    logger.debug("Received message for topic {}: {}".format( msg.topic, msg.payload.decode("utf-8")))

    data = None
    if msg.topic == "test":
        client.publish("response",'{"status": "received"}')

    try:
        data = json.loads(msg.payload.decode("UTF-8"))
    except json.JSONDecodeError as e:
        logger.error("JSON Decode Error: " + msg.payload.decode("UTF-8"))

    curr_topics = msg.topic.split("/")
    breakpoint()
    if msg.topic == "water/update":
        print("water update received")
        update_water(data)

    elif msg.topic == "connect/water":
        print("water meter connected")
        client.publish("connect/water/response", '{"total": "1234"}')

    elif curr_topics[0] == "battery":
        client.publish("response",'{"message": "battery"}')
        print("battery topic")
    #    mqtt_battery(data)

    #else:
    #    logger.error("Unhandled message topic {} with payload " + str(msg.topic, msg.payload.decode("utf-8")))




def signal_handler(sig, frame):
    """Capture Control+C and disconnect from Broker."""

    logger.info("You pressed Control + C. Shutting down, please wait...")

    client.disconnect() # Graceful disconnection.
    sys.exit(0)



def init_mqtt():
    global client

    # Our MQTT Client. See PAHO documentation for all configurable options.
    # "clean_session=True" means we don't want Broker to retain QoS 1 and 2 messages
    # for us when we're offline. You'll see the "{"session present": 0}" logged when
    # connected.
    client = mqtt.Client(                                                                      # (15)
        client_id=CLIENT_ID,
        clean_session=False)

    # Route Paho logging to Python logging.
    client.enable_logger()                                                                     # (16)

    # Setup callbacks
    client.on_connect = on_connect                                                             # (17)
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to Broker.
    client.connect(BROKER_HOST, BROKER_PORT)                                                   # (18)

def update_water(data):
    """ updates water consumption with data from MQTT payload
        payload must be formated as {"consumption": "1234"} """

    consumption = float(data["consumption"])
    last_water = session.query(Water).order_by(Water.timestamp.desc()).first()
    breakpoint()
    current_consumption = float(last_water.consumption) + consumption
    percent_consumed = (TANK_CAPACITY - current_consumption)/100
    percent_remain = 100 - percent_consumed

    new_water = Water(consumption = consumption, percent_remain = percent_remain )
    session.add(new_water)
    session.commit()

def mqtt_battery(payload):
    """ parses mqtt payloat and adds to db"""
    parsed_data = json.loads(payload)
    batt_data = Battery(volts = parsed_data.volts,
                        amps = parsed_data.current,
                        remain = parsed_data.residual_capacity,
                        percent = parsed_data.residual_capacity/parsed_data.nominal_capacity,
                        temp1 = parsed_data.temperature01,

                        )

# Initialise Module
init_mqtt()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Capture Control + C                        # (19)
    logger.info("Listening for messages on topic '" + ALL_TOPICS + "'. Press Control + C to exit.")

    client.loop_start()                                                                        # (20)
    signal.pause()
