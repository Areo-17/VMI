import os
import time
import pandas as pd
from datetime import datetime
from airflow.sdk import dag, task
from my_kafka.producer.producer import run_everything
from my_kafka.consumer.consumer import consumer_kafka
from utils.transformer import Transformer

def_args = {
    "owner":"Ariel",
    "start_date": datetime(2025, 11, 29)
}

@dag(dag_id = "VMI_001", default_args=def_args, schedule="@daily")

def etl_dag():

    @task
    def extract_producer():
        run_everything()
    
    @task
    def extract_consumer():
        consumer_kafka()

    @task
    def transform():
        BASE_PATH = os.path.dirname(os.path.abspath(__file__))
        FILE_PATH = os.path.abspath(os.path.join(BASE_PATH, "..", "data"))
        cleaning = Transformer(f'{FILE_PATH}/transportation.csv', f'{FILE_PATH}/processed.csv')
        data = cleaning.transformation()
        return data.to_json()

    @task
    def load(data_processed):
        BASE_PATH = os.path.dirname(os.path.abspath(__file__))
        FILE_PATH = os.path.abspath(os.path.join(BASE_PATH, "..", "data"))
        cleaned_file = pd.read_json(data_processed)
        load_file = Transformer(data=None, saving_path=f'{FILE_PATH}/processed.csv')
        load_file.loader(cleaned_file)

    e = extract_producer()
    e_2 = extract_consumer()
    t = transform()
    l = load(t)

    e >> e_2 >> t >> l

etl_dag()