# 🏭 Industrial IoT Data Pipeline

## 📌 Project Overview
This project simulates a complete end-to-end industrial data pipeline. It mocks a manufacturing press machine, captures its sensor data via OPC-UA, and streams it through a microservices architecture to a time-series database for real-time analytics.

**The Goal:** Demonstrate how to build a scalable pipeline that handles data generation, transport, enrichment, buffering, storage, and visualization.

---

## 🏗️ Architecture Stack
We use a "Bucket Brigade" pattern where data is passed and transformed at each stage:

1.  **Source:** `OPC-UA Server` (Python) - Simulates a machine generating Temp, Pressure, and Status.
2.  **Transport:** `MQTT` (Mosquitto) - Lightweight messaging protocol for the edge.
3.  **Enrichment:** `Redis` - In-memory cache used to inject static metadata (Location, Engineer ID) into the stream.
4.  **Buffer:** `Kafka` (Redpanda) - High-throughput event streaming platform to handle data spikes.
5.  **Storage:** `TimescaleDB` (PostgreSQL) - Time-series database optimized for sensor data.
6.  **Visualization:** `Grafana` - Dashboards for real-time monitoring and long-term trend analysis.

---

## 🚀 How to Run the Pipeline

1. **Start Infrastructure**
We use Docker for all backend services.

`docker-compose up -d`

Wait ~30 seconds for all containers (especially Redpanda and TimescaleDB) to fully initialize.

2. **Install Dependencies**
Make sure you have the required Python libraries:

`pip install -r requirements.txt`

3. **Initialize Data**

3.1. **Seed Redis:** Load static machine metadata such as 'Location' and 'Engineer' into the cache.

`python seed_redis.py`

3.2. **Database:** The table sensor_data and the view machine_1min_avg are created automatically via the init script. If not, run the SQL commands in "database/init.sql"

4. **Start the Agents**
Open 4 separate terminals and run the scripts in this specific order to see the data flow:

**Terminal 1 ( The Machine):** 
`python opcua-server/server.py`

**Terminal 2 (The Bridge):** 
`python agents/opcua-mqtt/agent.py`

**Terminal 3 (The Enricher):** 
`python agents/hydration/hydration_agent.py`

**Terminal 4 (The Database Sink):**  
`python agents/kafka-db/db_agent.py`

## 📊 Analytics & Visualization

**Grafana Dashboard**
URL: http://localhost:3000

**Login:** `admin / admin`

**Dashboard File:** Import dashboard.json (included in this repo) to see the pre-built layout.

### Key Visualizations
**1. Real-Time Sensor Feed (Panel 1):**

Visualizes raw data (sensor_data) as it arrives every 2 seconds.

Purpose: Immediate condition monitoring.

**2. Long-Term Trends (Panel 2):**

Visualizes the Continuous Aggregate (machine_1min_avg).

Purpose: Analyzing historical performance without querying millions of raw rows.

---

## 📘 Technical Reference

### Service Ports
| Service | Port | Description |
| :--- | :--- | :--- |
| **Grafana** | `3000` | Web Dashboard Interface |
| **Redpanda (Kafka)** | `19092` | External access for Agents |
| **Mosquitto (MQTT)** | `1883` | MQTT Broker Messaging Port |
| **TimescaleDB** | `5432` | PostgreSQL Database Access |
| **Redis** | `6379` | In-memory Cache |
| **OPC-UA Server** | `4840` | Simulation Server Endpoint |

### Database Schema (`sensor_data`)
The database uses a Hypertable optimized for time-series data.

| Column | Type | Description |
| :--- | :--- | :--- |
| `time` | `TIMESTAMPTZ` | **(Primary Key)** Timestamp of the sensor reading. |
| `machine_id` | `TEXT` | Unique identifier of the machine (e.g., "press_001"). |
| `temperature` | `FLOAT` | Core temperature reading (°C). |
| `pressure` | `FLOAT` | Internal pressure reading (bar). |
| `status` | `BOOLEAN` | Machine operational status (True=Running, False=Idle). |
| `location` | `TEXT` | Physical factory location (Enriched via Redis). |
| `engineer` | `TEXT` | Responsible engineer (Enriched via Redis). |

### Continuous Aggregate (`machine_1min_avg`)
A materialized view that pre-calculates metrics to speed up long-term trending.
* **Bucket Size:** 1 Minute
* **Metrics:** Average Temperature, Max Temperature, Average Pressure.