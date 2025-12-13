import json
import logging
import os
import redis
import paho.mqtt.client as mqtt
from kafka import KafkaProducer


# 1. LISTENS to the MQTT broker 
# 2. FETCHES context from Redis 
# 3. COMBINES them into one bigger message
# 4. SENDS the result to Kafka 

# Configuration
MQTT_BROKER = "localhost"
MQTT_TOPIC = "machine/data"
KAFKA_BROKER = "127.0.0.1:19092"  
KAFKA_TOPIC = "machine_enriched"

# Setup connections
# 1. Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 2. Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# 3. MQTT Callback 
def on_message(client, userdata, msg):
    try:
        # A. Decode the incoming MQTT message
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        
        # B. Get the static context from Redis
    
        context_str = r.get("machine_data")
        if context_str:
            context = json.loads(context_str)
            
            # C. Merge the two dictionaries
           
            data.update(context)
            
            # D. Send to Kafka
            producer.send(KAFKA_TOPIC, value=data)
            print(f"Hydrated & Sent to Kafka: {data}")
        else:
            print("Warning: No context found in Redis!")

    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    # Setup MQTT Client
    client = mqtt.Client()
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, 1883, 60)
        client.subscribe(MQTT_TOPIC)
        print(f"Hydration Agent Listening on {MQTT_TOPIC}...")
        
        # Start the loop to block and listen forever
        client.loop_forever()
        
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    main()