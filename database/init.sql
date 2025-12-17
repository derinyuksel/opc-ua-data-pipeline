-- Create the raw data table
CREATE TABLE IF NOT EXISTS sensor_data (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    machine_id TEXT,
    temperature DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    status BOOLEAN,
    location TEXT,
    engineer TEXT
);

-- Convert it into a TimescaleDB Hypertable
SELECT create_hypertable('sensor_data', 'time', if_not_exists => TRUE);

-- Create the Continuous Aggregate for analytics
CREATE MATERIALIZED VIEW IF NOT EXISTS machine_1min_avg
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 minute', time) AS bucket,
       machine_id,
       AVG(temperature) as avg_temp,
       MAX(temperature) as max_temp,
       AVG(pressure) as avg_press
FROM sensor_data
GROUP BY bucket, machine_id;

-- Added a refresh policy to update the aggregate automatically
SELECT add_continuous_aggregate_policy('machine_1min_avg',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute');