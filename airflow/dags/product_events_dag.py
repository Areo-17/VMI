import os
from datetime import datetime, timedelta
import pandas as pd

from airflow.sdk import dag, task
from airflow.exceptions import AirflowFailException

# Import your modules
from my_kafka.consumer.consumer import consumer_kafka
from utils.transformer import ProductEventTransformer
from my_kafka.producer.producer import KafkaProducerConf, KafkaStream


# ============================================================
# DEFAULT ARGS
# ============================================================
def_args = {
    "owner": "Student",
    "start_date": datetime(2025, 12, 5),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# ============================================================
# DAG
# ============================================================
@dag(
    dag_id="VMI_PRODUCT_EVENTS_ETL",
    default_args=def_args,
    schedule="@hourly",
    catchup=False,
    tags=["kafka", "product", "etl"]
)
def product_events_etl():

    # ------------------------------------------------------------
    # 1. EXTRACT (Simulate Produce -> Consume)
    # ------------------------------------------------------------
    @task
    def extract():
        # A. TRIGGER PRODUCER
        # Simulates real-time user activity on the website
        conf = KafkaProducerConf(bootstrap_servers="kafka:9092")
        ks = KafkaStream(conf)

        print("--> Generating real-time product events...")
        ks.run_single(
            duration_minutes=0.2,       # Run for 12 seconds
            event_name="product-events", # Target the new topic
            event_count=5               # Speed: 5 events/sec
        )

        # B. CONSUME
        # Consume specifically from the 'product-events' topic
        print("--> Consuming events...")
        raw_path = consumer_kafka(
            output_file="product_events_raw.csv",
            topics_list=["product-events"] 
        )

        if not raw_path or not os.path.exists(raw_path):
            raise AirflowFailException("Extract failed — no raw data file created.")

        return raw_path

    # ------------------------------------------------------------
    # 2. LOAD RAW
    # ------------------------------------------------------------
    @task
    def load_raw(raw_path: str):
        date_str = datetime.utcnow().strftime("%Y%m%d_%H%M")
        raw_dir = "/opt/airflow/data/raw_product"
        os.makedirs(raw_dir, exist_ok=True)

        dest_raw = f"{raw_dir}/events_{date_str}.csv"
        
        # Move/Copy data to Raw zone
        df = pd.read_csv(raw_path)
        df.to_csv(dest_raw, index=False)
        print(f"[LOAD] Raw product data archived → {dest_raw}")

        return dest_raw

    # ------------------------------------------------------------
    # 3. TRANSFORM & ANALYZE
    # ------------------------------------------------------------
    @task
    def transform(raw_saved: str):
        processed_dir = "/opt/airflow/data/processed_product"
        os.makedirs(processed_dir, exist_ok=True)

        processed_csv = f"{processed_dir}/product_events_clean.csv"

        # Initialize and run transformation
        transformer = ProductEventTransformer(
            data=raw_saved,
            saving_path=processed_csv
        )
        transformer.save() # This generates the Main CSV + KPI CSVs

        return processed_csv

    # ------------------------------------------------------------
    # FLOW
    # ------------------------------------------------------------
    raw_file = extract()
    archived_file = load_raw(raw_file)
    final_file = transform(archived_file)

    raw_file >> archived_file >> final_file

product_events_etl()