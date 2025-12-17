import asyncio
import json
import logging
from asyncua import Client
import paho.mqtt.client as mqtt


# Connects to the OPC-UA server as a CLIENT to read data.
# Connects to the MQTT Broker to PUBLISH that data.
# This decouples our source from the rest of the system.

# Configuration
OPCUA_URL = "opc.tcp://localhost:4840/freeopcua/server/"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "machine/data"

async def main():
    # Setup MQTT Connection
    # paho-mqtt to talk to the broker running in Docker.
    mqtt_client = mqtt.Client()
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"Failed to connect to MQTT: {e}")
        return

    # Setup OPC-UA Client
    async with Client(url=OPCUA_URL) as client:
        print(f"Connected to OPC-UA Server at {OPCUA_URL}")
        
        # We need to find the specific nodes we want to read.
        # These paths must match what we defined in server.py

        namespace = "http://examples.freeopcua.github.io"
        idx = await client.get_namespace_index(namespace)
        
        # Get the node objects so we can read them in the loop
        temp_node = await client.nodes.root.get_child(["0:Objects", f"{idx}:SimulatedMachine", f"{idx}:Temperature"])
        press_node = await client.nodes.root.get_child(["0:Objects", f"{idx}:SimulatedMachine", f"{idx}:Pressure"])
        status_node = await client.nodes.root.get_child(["0:Objects", f"{idx}:SimulatedMachine", f"{idx}:ProductionStatus"])

        while True:
            try:
                # Read Data from OPC-UA
                temp_val = await temp_node.read_value()
                press_val = await press_node.read_value()
                status_val = await status_node.read_value()

                # Format as JSON
               
                payload = {
                    "temperature": temp_val,
                    "pressure": press_val,
                    "status": status_val
                }
                json_payload = json.dumps(payload)

                # Publish to MQTT
           
                mqtt_client.publish(MQTT_TOPIC, json_payload)
                
                print(f"Sent to MQTT: {json_payload}")
                
            except Exception as e:
                print(f"Error reading/publishing: {e}")

            # Wait 2 seconds before the next reading
            await asyncio.sleep(2)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    asyncio.run(main())