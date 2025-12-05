import os
import requests
import json
import random
import logging
import sys
import time
from dataclasses import dataclass
from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import uuid
from datetime import datetime

load_dotenv()

MOCK_API = os.environ.get('MOCKAROO_API')

# Determine output path for files/logs. Prefer explicit env var `TRANSPORT_OUTPUT_PATH`,
# otherwise use Airflow's shared data folder `/opt/airflow/data` so files persist on host.
OUTPUT_PATH = os.environ.get('TRANSPORT_OUTPUT_PATH') or os.path.join(
    os.environ.get('AIRFLOW_HOME', '/opt/airflow'), 'data'
)
try:
    os.makedirs(OUTPUT_PATH, exist_ok=True)
except Exception:
    # If cannot create (permissions), proceed and let logging module handle errors
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # ARCHIVO: Para análisis histórico y troubleshooting
        logging.FileHandler(os.path.join(OUTPUT_PATH, 'producer.log'), encoding="utf-8"),
        # CONSOLA: Para feedback inmediato durante desarrollo
        logging.StreamHandler(sys.stdout)
    ]
)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding= 'utf-8')
    sys.stderr.reconfigure(encoding= 'utf-8')

logger = logging.getLogger(__name__)

# ---------------------- Data generation using Mockaroo's API ---------------- #

class MockData:

    mock_url = "https://api.mockaroo.com/api/generate"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_data(self, fields: list, count: int, format_: str = "json"):
        petition = requests.post(
            url=self.mock_url,
            params={
                "key": self.api_key,
                "count": count,
                "format": format_,
                "include_nulls": True
            },
            json=fields
        )

        if petition.status_code != 200:
            return "Mockaroo API not responding"
        if format_ == "json":
            petition.json()
        
        return petition.text
    
    def create_payload() -> dict:
        
        client = MockData(MOCK_API)

        content_schema = [
        {
            "name": "transaction_id",
            "type": "GUID"
        },
        {
            "name": "transaction_date",
            "type": "Datetime",
            "min": "11/01/2025",
            "max":"11/24/2025",
            "format":"%Y/%m/%d"
        },
        {
            "name": "transaction_time",
            "type": "Time",
            "min": "05:00 AM",
            "max": "23:00 PM",
            "format": "%H:%M:%S"
        },
        {
            "name": "is_va_y_ven_system",
            "type": "Formula",
            "value": "transaction_date >= '2021/11/27'"
        },
        {
            "name": "service_provider",
            "type": "Formula",
            "value": "is_va_y_ven_system ? 'Va-y-Ven (ATY)' : 'Traditional Bus Company'"
        },
        {
            "name": "routes_vayven",
            "type": "Custom List",
            "values": [
            'Urban/Metropolitan Circuito',
            'Ie-Tram Corridor'
            ]
        },
        {
            "name": "routes_alt",
            "type": "Custom List",
            "values": [
            'Urban/Feeder Route',
            'Suburban/Connecting Route'
            ]
        },
        {
            "name": "route_type",
            "type": "Formula",
            "value": "is_va_y_ven_system ? routes_vayven : routes_alt"
        },
        {
            "name": "boarding_area",
            "type": "Custom List",
            "values": [
            "Centro (Downtown)",
            "North Zone (Altabrisa/Montejo)",
            "West Zone (Caucel/Juan Pablo II)",
            "East Zone (Vergel/Kanasín)",
            "South Zone (Emiliano Zapata Sur/San Haroldo)",
            "Circuito Route Stop"
            ],
            "weights": [35, 15, 15, 15, 10, 10]
        },
        {
            "name": "alighting_area",
            "type": "Custom List",
            "values": [
            "Centro (Downtown)",
            "North Zone (Altabrisa/Montejo)",
            "West Zone (Caucel/Juan Pablo II)",
            "East Zone (Vergel/Kanasín)",
            "South Zone (Emiliano Zapata Sur/San Haroldo)",
            "University/School/Work Area"
            ],
            "weights": [25, 15, 15, 15, 10, 20]
        },
        {
            "name": "payment_method",
            "type": "Custom List",
            "values": ["QR", "Card"],
            "weights": [15, 85]
        },
        {
            "name": "fare_type",
            "type": "Custom List",
            "values": ["Regular", "Student/Senior/Disability"],
            "weights": [60, 40]
        },
        {
            "name": "alt_fare_amount",
            "type": "Custom List",
            "values": ["5", "2.50", "0"]
        },
        {
            "name": "fare_amount_mxn",
            "type": "Formula",
            "value": "fare_type == 'Regular' ? 12 : payment_method == 'QR' ? 12 : alt_fare_amount"
        },
        {
            "name": "trip_duration_minutes",
            "type": "Formula",
            "value": "route_type == 'Urban/Metropolitan Circuito' ? random(30, 90) : (route_type == 'Urban/Feeder Route' ? random(15, 60) : (route_type == 'Ie-Tram Corridor' ? random(10, 45) : random(45, 120)))"
        },
        {
            "name": "is_peak_hour",
            "type": "Formula",
            "value": "((time(transaction_time) >= '6' && time(transaction_time) <= '9') || (time(transaction_time) >= '17' && time(transaction_time) <= '20'))"
        },
        {
            "name": "passenger_count",
            "type": "Formula",
            "value": "is_va_y_ven_system ? random(0,85) : 1"
        }
        ]

        payload = client.generate_data(fields = content_schema, count = 1, format_ = "json")
        payload_list = json.loads(payload)
        # Mockaroo returns a list when count>1; we request 1 so take first element
        if isinstance(payload_list, list) and len(payload_list) > 0:
            return payload_list[0]
        return payload_list

def make_local_payload() -> dict:
    """Generate a small deterministic payload for local development when
    Mockaroo API key is not available."""
    now = datetime.utcnow()
    return {
        "transaction_id": str(uuid.uuid4()),
        "transaction_date": now.strftime("%Y/%m/%d"),
        "transaction_time": now.strftime("%H:%M:%S"),
        "is_va_y_ven_system": True,
        "service_provider": "Va-y-Ven (ATY)",
        "routes_vayven": "Urban/Metropolitan Circuito",
        "routes_alt": "Urban/Feeder Route",
        "route_type": "Urban/Metropolitan Circuito",
        "boarding_area": "Centro (Downtown)",
        "alighting_area": "Centro (Downtown)",
        "payment_method": "QR",
        "fare_type": "Regular",
        "alt_fare_amount": "5",
        "fare_amount_mxn": 12,
        "trip_duration_minutes": 30,
        "passenger_count": 1
    }
    
# ---------------------- Kafka producer configuration ------------------------ #
@dataclass
class KafkaProducerConf:

    bootstrap_servers: str = "localhost:9092"

    # Batch size value is defined in bytes
    batch_size: int = 32000

    # Latency. While higher the value, bigger the throughput but higher the lattency.
    linger_ms = 8

    # Producer buffer, also in bytes.
    buffer_memory : int = 32000000

    # Compression. It indicates the compression algorithm in which the messages will be compressed in order to reduced its size and be sent.
    compression_type : str = "gzip"
    
# ---------------------- Kafka producer development ------------------------ #

class KafkaStream:

    def __init__(self, config: KafkaProducerConf):
        self.config = config
    
        self.producer = self._initiate_kafka_producer()
        # Use MockData when MOCKAROO_API is set, otherwise use a local generator
        if MOCK_API:
            self.generator = MockData
            self.topics = {"transportation-stats": self.generator.create_payload}
        else:
            self.generator = None
            self.topics = {"transportation-stats": make_local_payload}

    def _initiate_kafka_producer(self) -> KafkaProducer:
        
        try: 
            producer = KafkaProducer(
            
            bootstrap_servers = self.config.bootstrap_servers,
            batch_size = self.config.batch_size,
            value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8') if x else None,
            linger_ms = self.config.linger_ms,
            buffer_memory = self.config.buffer_memory,
            compression_type = self.config.compression_type,
            retries = 3,
            acks = 'all'
            )
        
            logger.info(f"Successfully connected to kafka producers in {self.config.bootstrap_servers}")
            return producer
        
        except KafkaError as e:
            logger.info(f'Could not connect to Kafka producer due to {e}')
            raise

    def send_data(self, my_topic: str, event: dict):
        try:
            future = self.producer.send(
                topic = my_topic,
                value = event,
                key = event.get('transaction_id')
            )

            future.add_callback(self.successful_sent)


            future.add_errback(self.failed_event)

        except Exception as e:
           logger.error(f"Failed to sent the event to the topic {my_topic} due to {e}")
    
    def successful_sent(self, record_metadata):
        logger.debug(f"The event was successfully to the topic {record_metadata.topic} in the partition {record_metadata.partition}")

    def failed_event(self, exception):
        logger.debug(f"The event could not be sent. Error {exception}")

    def run_producer(self, duration: float = 0.1, event_name: str = 'transportation-stats', event_count: int = 2):

        event_generation = self.topics[event_name]
        end_time = time.time() + (duration * 60)
        generation_interval = 1 / event_count
        try:
            while time.time() <= end_time:
                event = event_generation()
                self.send_data(event_name, event)

                logger.info(f"Event sent with the following information: {event}")

                time.sleep(generation_interval)
        except KeyboardInterrupt:
            logger.info("Events sending stopped by the user.")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up producer resources...")
        self.producer.flush()  # Ensure all messages are sent
        self.producer.close()
        logger.info("Producer shutdown complete")

def run_everything():
    
    config = KafkaProducerConf(bootstrap_servers="kafka:9092")
    producer = KafkaStream(config)

    producer.run_producer()

if __name__ == '__main__':
    
    run_everything()
