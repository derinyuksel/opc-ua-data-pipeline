import json
import logging
import psycopg2
from kafka import KafkaConsumer


# Configuration
KAFKA_BROKER = "127.0.0.1:19092"
KAFKA_TOPIC = "machine_enriched"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "iot_data"
DB_USER = "postgres"
DB_PASS = "password"

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def main():
    # 1. Connect to Kafka
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    # 2. Connect to Database
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print(f"Connected to Database {DB_NAME}...")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return

    print(f"Listening to Kafka topic: {KAFKA_TOPIC}...")

    # 3. Consume & Insert Loop
    for message in consumer:
        try:
            data = message.value
            
            # Prepare the SQL query
            query = """
                INSERT INTO sensor_data (machine_id, temperature, pressure, status, location, engineer)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                data.get("machine_id"),
                data.get("temperature"),
                data.get("pressure"),
                data.get("status"),
                data.get("location"),
                data.get("engineer")
            )
            
            # Execute and Commit
            cur.execute(query, values)
            conn.commit()
            
            print(f"Saved to DB: {data['temperature']}°C | {data['pressure']} bar")

        except Exception as e:
            print(f"Error inserting data: {e}")
            # Try to reconnect if DB connection dropped
            conn = get_db_connection()
            cur = conn.cursor()

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    main()