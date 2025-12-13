import redis
import json


# This is a helper script to seed our Redis database.
# In a real factory, this database would contain info about hundreds of machines.
# For us, we just add info for our one "SimulatedMachine".

# Connect to Redis running in Docker
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Define the static info for our machine
machine_info = {
    "machine_id": "press_001",
    "location": "Factory_Floor_A",
    "engineer": "Felix Salcher"
}

# Save it to Redis under the key "machine_data"
# We store it as a JSON string so we can parse it easily later.
r.set("machine_data", json.dumps(machine_info))

print("✅ Redis has been seeded with machine data!")
print(f"Stored: {r.get('machine_data')}")