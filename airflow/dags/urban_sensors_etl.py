import os
from datetime import datetime, timedelta
import pandas as pd

from airflow.sdk import dag, task
from airflow.exceptions import AirflowFailException

from my_kafka.consumer.consumer import consumer_kafka
from utils.transformer import UrbanSensorTransformer
from my_kafka.producer.producer import KafkaProducerConf, KafkaStream


# ============================================================
# DEFAULT ARGS
# ============================================================
def_args = {
    "owner": "Ariel",
    "start_date": datetime(2025, 12, 5),
    "retries": 2,                        # requirement: task retries
    "retry_delay": timedelta(minutes=2),
}


# ============================================================
# DAG
# ============================================================
@dag(
    dag_id="VMI_URBAN_SENSORS_ETL",
    default_args=def_args,
    schedule="@hourly",
    catchup=False
)
def urban_sensors_etl():

    # ------------------------------------------------------------
    # 1. EXTRACT
    # ------------------------------------------------------------
    @task
    def extract():

        conf = KafkaProducerConf(bootstrap_servers="kafka:9092")
        ks = KafkaStream(conf)

        # run only urban-sensors
        ks.run_single(
            duration_minutes=0.1,
            event_name="urban-sensors",
            event_count=2
        )

        raw_path = consumer_kafka(output_file="urban_sensors_raw.csv")

        if not raw_path or not os.path.exists(raw_path):
            raise AirflowFailException("Extract step failed — no raw data file created.")

        return raw_path


    # ------------------------------------------------------------
    # 2. LOAD (save RAW dataset)
    # ------------------------------------------------------------
    @task
    def load_raw(raw_path: str):

        # destination in raw zone
        date_str = datetime.utcnow().strftime("%Y%m%d_%H%M")
        raw_dir = "/opt/airflow/data/raw"
        os.makedirs(raw_dir, exist_ok=True)

        dest_raw = f"{raw_dir}/urban_sensors_raw_{date_str}.csv"

        df = pd.read_csv(raw_path)
        df.to_csv(dest_raw, index=False)

        print(f"[LOAD] Raw data saved → {dest_raw}")

        return dest_raw


    # ------------------------------------------------------------
    # 3. TRANSFORM (single task)
    # ------------------------------------------------------------
    @task
    def transform(raw_saved: str):

        processed_dir = "/opt/airflow/data/processed"
        analytics_dir = "/opt/airflow/data/analytics"

        os.makedirs(processed_dir, exist_ok=True)
        os.makedirs(analytics_dir, exist_ok=True)

        processed_csv = f"{processed_dir}/urban_sensors_processed.csv"
        analytics_parquet = f"{analytics_dir}/urban_sensors_processed.parquet"

        # --- run ALL transformations here ---
        transformer = UrbanSensorTransformer(
            data=raw_saved,
            saving_path=processed_csv
        )
        transformer.save()                  # saves CSV + aggregated CSV

        # Save a Parquet version (analytics layer)
        df = pd.read_csv(processed_csv)
        df.to_parquet(analytics_parquet, index=False)

        print(f"[TRANSFORM] Processed CSV → {processed_csv}")
        print(f"[TRANSFORM] Parquet analytics → {analytics_parquet}")

        return processed_csv


    # ------------------------------------------------------------
    # FLOW: Extract → Load → Transform
    # ------------------------------------------------------------
    raw = extract()
    raw_saved = load_raw(raw)
    processed = transform(raw_saved)

    raw >> raw_saved >> processed


urban_sensors_etl()