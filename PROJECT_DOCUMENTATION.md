# 📘 Project Documentation

## 1. OPC-UA Server Overview
The simulation server mimics an industrial Press Machine located on the factory floor. It exposes the following nodes under the namespace `http://examples.freeopcua.github.io`:

| Node Name | Data Type | Access | Description |
| :--- | :--- | :--- | :--- |
| **Temperature** | `Double` | Read-Only | Represents the core operating temperature of the machine (simulated range: 20.0 - 80.0 °C). |
| **Pressure** | `Double` | Read-Only | Represents the hydraulic pressure applied by the press (simulated range: 1000.0 - 1050.0 bar). |
| **ProductionStatus** | `Boolean` | Read-Only | Indicates the operational state. `True` signifies normal production; `False` indicates a stop or error state (10% probability). |

---

## 2. System Architecture

### User Interfaces & Endpoints
* **Grafana Dashboard:** [http://localhost:3000](http://localhost:3000) (Login: `admin` / `admin`)
* **Redpanda (Kafka) Broker:** `localhost:19092` (Accessible externally via the `kafka-db` and `hydration` agents)
* **MQTT Broker:** `localhost:1883` (Accepts anonymous connections)

### Service Port Mapping
The system uses the following ports for inter-service and external communication:

| Service | Container Port | Host Port | Protocol | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Mosquitto** | `1883` | `1883` | TCP/MQTT | Ingests data from the Bridge Agent. |
| **Redis** | `6379` | `6379` | TCP | Serves cached metadata for stream enrichment. |
| **Redpanda** | `19092` | `19092` | TCP | External Kafka listener for Windows host access. |
| **TimescaleDB** | `5432` | `5432` | TCP/Postgres | Persistent storage for sensor data. |
| **Grafana** | `3000` | `3000` | HTTP | Web interface for data visualization. |
| **OPC-UA Server**| `4840` | `4840` | OPC.TCP | Endpoint for the Simulation Server. |

---

## 3. Database Schema
Data is stored in **TimescaleDB** (PostgreSQL extension) in a hypertable named `sensor_data`.

| Column | Type | Description |
| :--- | :--- | :--- |
| `time` | `TIMESTAMPTZ` | **Primary Key (Partition Key)**. The exact timestamp when the sensor reading was generated. |
| `machine_id` | `TEXT` | A unique identifier for the machine (e.g., `press_001`). Enriched from Redis. |
| `temperature` | `DOUBLE PRECISION`| The raw temperature value from the sensor. |
| `pressure` | `DOUBLE PRECISION`| The raw pressure value from the sensor. |
| `status` | `BOOLEAN` | The machine status (`True`=Running). |
| `location` | `TEXT` | The physical location of the machine (e.g., `Factory_Floor_A`). Enriched from Redis. |
| `engineer` | `TEXT` | The name of the engineer responsible for this unit. Enriched from Redis. |

---

## 4. Continuous Aggregate Details
To optimize long-term queries, a **Materialized View** named `machine_1min_avg` is maintained by TimescaleDB.

* **Configuration:**
    * **Bucket Size:** `1 minute`
    * **Refresh Policy:** Continuous (updates automatically as new data arrives).
* **Metrics Computed:**
    1.  **`avg_temp`**: The average temperature over the 1-minute bucket.
    2.  **`max_temp`**: The highest temperature recorded in that minute.
    3.  **`avg_press`**: The average pressure over the 1-minute bucket.
* **Purpose:** This reduces the read load on the database for historical dashboards. Instead of averaging 30 rows (one every 2s) per minute at query time, the database pre-calculates a single row.

---

## 5. Grafana Configuration
The dashboard **"IoT Data Pipeline Dashboard"** consists of two primary panels:

### Panel 1: Real-Time Sensor Data
* **Visualization Type:** Time Series Chart
* **Data Source:** `sensor_data` (Hypertable)
* **Query:**
    ```sql
    SELECT time AS "time", temperature
    FROM sensor_data
    WHERE $__timeFilter(time)
    ORDER BY 1
    ```
* **Interpretation:** Displays raw, granular data points arriving every 2 seconds. Used for monitoring immediate fluctuations and identifying sudden spikes in temperature or pressure.

### Panel 2: Long-Term Trends (1-min Avg)
* **Visualization Type:** Time Series Chart
* **Data Source:** `machine_1min_avg` (Continuous Aggregate)
* **Query:**
    ```sql
    SELECT bucket AS "time", avg_temp
    FROM machine_1min_avg
    WHERE $__timeFilter(bucket)
    ORDER BY 1
    ```
* **Interpretation:** Displays a smoothed trend line with one data point per minute. This is ideal for viewing performance over longer periods (hours or days) without visual noise.