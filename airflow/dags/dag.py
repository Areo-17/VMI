import os
import json
import time
import pandas as pd
from datetime import datetime
from airflow.sdk import dag, task
from airflow.exceptions import AirflowFailException
from my_kafka.consumer.consumer import consumer_kafka
from utils.transformer import Transformer
from my_kafka.producer.producer import KafkaProducerConf, KafkaStream

def_args = {
    "owner":"Ariel",
    "start_date": datetime(2025, 11, 29)
}

@dag(dag_id = "VMI_001", default_args=def_args, schedule="@daily")

def etl_dag():

    @task
    def extract_producer():

        conf = KafkaProducerConf(bootstrap_servers="kafka:9092")
        ks = KafkaStream(conf)

        # run only urban-sensors
        ks.run_single(
            duration_minutes=0.1,
            event_name="transportation-stats",
            event_count=2
        )

        raw_csv = consumer_kafka(output_file='transportation.csv')

        if not raw_csv or not os.path.exists(raw_csv):
            raise AirflowFailException("Extract step failed. No transportation-stats CSV found.")

        return raw_csv
    
    @task
    def extract_consumer():
        # Run consumer and return the path to the CSV it creates
        return consumer_kafka()

    @task
    def transform(consumed_path: str):
        # If the consumer returned a path, use it. Otherwise fallback to standard path.
        if consumed_path:
            input_path = consumed_path
        else:
            input_path = '/opt/airflow/data/transportation.csv'

        # Wait loop remains the same...

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"The path {input_path} does not exist. Check the string typed.")

        FILE_PATH = '/opt/airflow/data'
        output_path = f'{FILE_PATH}/processed.csv'
        
        # 1. Instantiate the Transformer for cleaning
        cleaning = Transformer(input_path, output_path)
        data_cleaned = cleaning.transformation()
        
        # 2. Instantiate a loader (or use a simple pandas save, but using your class is fine)
        # Note: We must pass the output_path as the saving_path here.
        loader = Transformer(data=None, saving_path=output_path)
        loader.loader(data_cleaned)
        
        # 3. Return the path to the saved file (small string, good for XCom)
        return output_path # <-- Returns '/opt/airflow/data/processed.csv'

    @task
    def load(data_processed_path: str): # <-- Receives the path string
        # Re-read the saved file. This task can now be focused on actual loading 
        # to a database, cloud storage, etc.
        
        cleaned_file = pd.read_csv(data_processed_path)
        
        # Save processed data into the shared data folder so it persists on host
        FILE_PATH = '/opt/airflow/data'
        load_file = Transformer(data=None, saving_path=f'{FILE_PATH}/final_data_warehouse_output.csv')
        load_file.loader(cleaned_file)
        
        print(f"Final data loaded from disk path: {data_processed_path}")

    e = extract_producer()
    e_2 = extract_consumer()
    t = transform(e_2)
    l = load(t)

    # Enforce sequential execution: producer → consumer → transform → load
    e >> e_2 >> t >> l

etl_dag()