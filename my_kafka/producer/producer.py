#!/usr/bin/env python3
import os
import requests
import json
import random
import logging
import sys
import time
import threading
from dataclasses import dataclass
from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka.errors import KafkaError
import uuid
from datetime import datetime, timezone

load_dotenv()

MOCK_API = os.environ.get('MOCKAROO_API')

OUTPUT_PATH = os.environ.get('TRANSPORT_OUTPUT_PATH') or os.path.join(
    os.environ.get('AIRFLOW_HOME', '/opt/airflow'), 'data'
)
try:
    os.makedirs(OUTPUT_PATH, exist_ok=True)
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_PATH, 'producer.log'), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)

# ---------------------- Mockaroo-based generator (keeps original behavior) ---------------- #
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
            json=fields,
            timeout=10
        )

        if petition.status_code != 200:
            raise RuntimeError(f"Mockaroo returned {petition.status_code}: {petition.text}")
        return petition.text

    @staticmethod
    def create_payload() -> dict:
        
        client = MockData(MOCK_API)

        content_schema = [
            {"name": "transaction_id", "type": "GUID"},
            {"name": "transaction_date", "type": "Datetime", "min": "11/01/2025", "max": "11/24/2025", "format": "%Y/%m/%d"},
            {"name": "transaction_time", "type": "Time", "min": "05:00 AM", "max": "23:00 PM", "format": "%H:%M:%S"},
            {"name": "is_va_y_ven_system", "type": "Formula", "value": "transaction_date >= '2021/11/27'"},
            {"name": "service_provider", "type": "Formula", "value": "is_va_y_ven_system ? 'Va-y-Ven (ATY)' : 'Traditional Bus Company'"},
            {"name": "routes_vayven", "type": "Custom List", "values": ['Urban/Metropolitan Circuito', 'Ie-Tram Corridor']},
            {"name": "routes_alt", "type": "Custom List", "values": ['Urban/Feeder Route', 'Suburban/Connecting Route']},
            {"name": "route_type", "type": "Formula", "value": "is_va_y_ven_system ? routes_vayven : routes_alt"},
            {"name": "boarding_area", "type": "Custom List", "values": ["Centro (Downtown)", "North Zone (Altabrisa/Montejo)", "West Zone (Caucel/Juan Pablo II)", "East Zone (Vergel/Kanasín)", "South Zone (Emiliano Zapata Sur/San Haroldo)", "Circuito Route Stop"], "weights": [35, 15, 15, 15, 10, 10]},
            {"name": "alighting_area", "type": "Custom List", "values": ["Centro (Downtown)", "North Zone (Altabrisa/Montejo)", "West Zone (Caucel/Juan Pablo II)", "East Zone (Vergel/Kanasín)", "South Zone (Emiliano Zapata Sur/San Haroldo)", "University/School/Work Area"], "weights": [25, 15, 15, 15, 10, 20]},
            {"name": "payment_method", "type": "Custom List", "values": ["QR", "Card"], "weights": [15, 85]},
            {"name": "fare_type", "type": "Custom List", "values": ["Regular", "Student/Senior/Disability"], "weights": [60, 40]},
            {"name": "alt_fare_amount", "type": "Custom List", "values": ["5", "2.50", "0"]},
            {"name": "fare_amount_mxn", "type": "Formula", "value": "fare_type == 'Regular' ? 12 : payment_method == 'QR' ? 12 : alt_fare_amount"},
            {"name": "trip_duration_minutes", "type": "Formula", "value": "route_type == 'Urban/Metropolitan Circuito' ? random(30, 90) : (route_type == 'Urban/Feeder Route' ? random(15, 60) : (route_type == 'Ie-Tram Corridor' ? random(10, 45) : random(45, 120)))"},
            {"name": "is_peak_hour", "type": "Formula", "value": "((time(transaction_time) >= '6' && time(transaction_time) <= '9') || (time(transaction_time) >= '17' && time(transaction_time) <= '20'))"},
            {"name": "passenger_count", "type": "Formula", "value": "is_va_y_ven_system ? random(0,85) : 1"}
        ]

        payload = client.generate_data(fields=content_schema, count=1, format_="json")
        payload_list = json.loads(payload)
        if isinstance(payload_list, list) and len(payload_list) > 0:
            return payload_list[0]
        return payload_list

def make_local_payload() -> dict:
    now = datetime.now(timezone.utc)
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

# ---------------------- New synthetic urban-sensor generator ----------------- #
def make_urban_sensor_payload() -> dict:
    """Generates a synthetic urban sensor payload (traffic, noise, air quality)."""
    now = datetime.now(timezone.utc)
    return {
        "sensor_id": f"sensor-{random.randint(100,999)}",
        "ts": now.isoformat(),
        "location": random.choice(["Centro", "Altabrisa", "Caucel", "Kanasin", "Emiliano Zapata"]),
        "vehicle_count": random.randint(0, 200),
        "avg_speed_kmh": round(random.uniform(0, 80), 2),
        "noise_db": round(random.uniform(30, 100), 1),
        "pm25": round(random.uniform(1, 150), 2),
        "pm10": round(random.uniform(5, 200), 2),
        "status": random.choice(["OK", "MAINTENANCE", "OFFLINE"])
    }

# ---------------------- New Product Event Generator ----------------- #
class ProductEventGenerator:
    """
    Generates realistic product interaction events (views, cart, purchase).
    Uses standard libraries to ensure compatibility without extra pip installs.
    """
    
    PRODUCTS = {
        "electronics": [
            {"name": "Laptop Pro", "price": 1200},
            {"name": "Smartwatch X", "price": 250},
            {"name": "Wireless Buds", "price": 150},
            {"name": "4K Monitor", "price": 400}
        ],
        "clothing": [
            {"name": "Denim Jeans", "price": 60},
            {"name": "Cotton T-Shirt", "price": 25},
            {"name": "Sneakers", "price": 90},
            {"name": "Winter Jacket", "price": 120}
        ],
        "home": [
            {"name": "Coffee Maker", "price": 80},
            {"name": "Blender 3000", "price": 50},
            {"name": "Smart Bulb", "price": 15}
        ]
    }
    
    EVENT_TYPES = ["product_view", "add_to_cart", "remove_from_cart", "purchase"]
    # Weights simulate a funnel: lots of views, fewer cart adds, even fewer purchases
    EVENT_WEIGHTS = [0.65, 0.20, 0.10, 0.05] 

    def __init__(self):
        # Flatten products for easy random selection
        self.all_products = []
        for cat, items in self.PRODUCTS.items():
            for item in items:
                item_copy = item.copy()
                item_copy['category'] = cat
                item_copy['id'] = str(uuid.uuid4())[:8]
                self.all_products.append(item_copy)
        
        # Simulate a pool of active users
        self.users = [f"user_{i:04d}" for i in range(1, 200)]

    def generate(self) -> dict:
        """Generates a single product interaction event."""
        
        user_id = random.choice(self.users)
        product = random.choice(self.all_products)
        event_type = random.choices(self.EVENT_TYPES, weights=self.EVENT_WEIGHTS, k=1)[0]
        now = datetime.now(timezone.utc)
        
        payload = {
            "event_id": str(uuid.uuid4()),
            "timestamp": now.isoformat(),
            "user_id": user_id,
            "session_id": f"sess_{hash(user_id) + now.hour}", # Simple session sim
            "event_type": event_type,
            "product_id": product['id'],
            "product_name": product['name'],
            "category": product['category'],
            "price": product['price'],
            "platform": random.choice(["web", "ios", "android"]),
        }
        
        # Add context specific fields
        if event_type == "purchase":
            payload["purchase_amount"] = product['price']
            payload["payment_method"] = random.choice(["credit_card", "paypal", "apple_pay"])
        
        return payload

# ---------------------- Kafka producer configuration ------------------------ #
@dataclass
class KafkaProducerConf:
    bootstrap_servers: str = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
    batch_size: int = 32000
    linger_ms: int = 8
    buffer_memory: int = 32000000
    compression_type: str = "gzip"

# ---------------------- KafkaStream with multistream support ----------------- #
class KafkaStream:
    def __init__(self, config: KafkaProducerConf):
        self.config = config
        self.producer = self._initiate_kafka_producer()

        # Initialize the product generator
        self.product_gen = ProductEventGenerator()

        # topics mapping can be extended via env var TOPICS (comma separated)
        # Default set now includes product-events
        env_topics = os.environ.get("TOPICS")
        if env_topics:
            topic_list = [t.strip() for t in env_topics.split(",") if t.strip()]
        else:
            topic_list = ["transportation-stats", "urban-sensors", "product-events"]

        # map topic -> generator callable
        self.topics = {}
        for t in topic_list:
            if t == "transportation-stats":
                # use MockData if available, otherwise local static payload
                self.topics[t] = MockData.create_payload if MOCK_API else make_local_payload
            elif t == "urban-sensors":
                self.topics[t] = make_urban_sensor_payload
            elif t == "product-events":
                self.topics[t] = self.product_gen.generate
            else:
                # fallback generator: small generic event
                self.topics[t] = lambda: {"id": str(uuid.uuid4()), "ts": datetime.now(timezone.utc).isoformat(), "topic": t}

        logger.info(f"Configured topics: {list(self.topics.keys())}")

    def _initiate_kafka_producer(self) -> KafkaProducer:
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.config.bootstrap_servers,
                batch_size=self.config.batch_size,
                value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None,
                linger_ms=self.config.linger_ms,
                buffer_memory=self.config.buffer_memory,
                compression_type=self.config.compression_type,
                retries=3,
                acks='all'
            )
            logger.info(f"Successfully connected to kafka producers in {self.config.bootstrap_servers}")
            return producer
        except KafkaError as e:
            logger.exception('Could not connect to Kafka producer')
            raise

    def send_data(self, my_topic: str, event: dict):
        try:
            future = self.producer.send(
                topic=my_topic,
                value=event,
                key=event.get('transaction_id') if isinstance(event, dict) else None
            )
            future.add_callback(self.successful_sent)
            future.add_errback(self.failed_event)
        except Exception as e:
            logger.exception(f"Failed to send event to topic {my_topic}: {e}")

    def successful_sent(self, record_metadata):
        logger.debug(f"Sent to topic={record_metadata.topic} partition={record_metadata.partition}")

    def failed_event(self, exception):
        logger.debug(f"Send failed: {exception}")

    def _produce_loop(self, topic: str, duration_minutes: float, event_count: int, stop_event: threading.Event):
        """Run a single stream producing events for duration_minutes (float)."""
        generator = self.topics.get(topic)
        if not generator:
             logger.warning(f"No generator found for topic {topic}, skipping.")
             return

        end_time = time.time() + duration_minutes * 60
        interval = 1.0 / max(1, event_count)
        logger.info(f"Starting producer for topic={topic} interval={interval}s until {time.ctime(end_time)}")
        try:
            while not stop_event.is_set() and time.time() <= end_time:
                try:
                    event = generator()
                except Exception as e:
                    logger.warning(f"Generator for topic {topic} raised {e}; skipping this event")
                    event = {"error": str(e), "topic": topic, "ts": datetime.now(timezone.utc).isoformat()}
                self.send_data(topic, event)
                logger.info(f"[{topic}] event -> {event}")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info(f"Producer thread for {topic} interrupted by user.")
        finally:
            logger.info(f"Producer for topic={topic} exiting loop.")

    def run_multistream(self, streams: list, duration_minutes: float = 0.1, event_count: int = 2):
        """
        streams: list of topic names or tuples (topic, event_count) to run concurrently.
        duration_minutes: total minutes each thread will run.
        event_count: events per second per stream (if per-stream not provided).
        """
        stop_event = threading.Event()
        threads = []
        # Normalize streams entries
        normalized = []
        for s in streams:
            if isinstance(s, (list, tuple)) and len(s) >= 1:
                topic = s[0]
                ec = s[1] if len(s) > 1 else event_count
                normalized.append((topic, int(ec)))
            else:
                normalized.append((s, event_count))

        for topic, ec in normalized:
            if topic not in self.topics:
                logger.warning(f"Topic {topic} not configured; skipping")
                continue
            t = threading.Thread(target=self._produce_loop, args=(topic, duration_minutes, ec, stop_event), daemon=True)
            threads.append(t)
            t.start()

        try:
            # join threads until they finish
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received — signalling threads to stop")
            stop_event.set()
        finally:
            self._cleanup()

    def run_single(self, duration_minutes: float = 0.1, event_name: str = 'transportation-stats', event_count: int = 2):
        self.run_multistream([ (event_name, event_count) ], duration_minutes=duration_minutes, event_count=event_count)

    def _cleanup(self):
        logger.info("Cleaning up producer resources...")
        try:
            self.producer.flush()
            self.producer.close()
        except Exception:
            pass
        logger.info("Producer shutdown complete")


def run_from_cli():
    import argparse
    parser = argparse.ArgumentParser(description="Kafka multistream producer")
    parser.add_argument("--bootstrap", default=os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092"))
    # Updated default streams to include the new product-events topic
    parser.add_argument("--streams", default=os.environ.get("TOPICS", "transportation-stats,urban-sensors,product-events"),
                        help="Comma-separated topics or topic:rate pairs (rate=events_per_second)")
    parser.add_argument("--duration", type=float, default=float(os.environ.get("PRODUCER_DURATION_MIN", 0.1)),
                        help="Duration in minutes for each stream")
    parser.add_argument("--rate", type=int, default=int(os.environ.get("PRODUCER_RATE", 2)),
                        help="Default events per second per stream")
    args = parser.parse_args()

    conf = KafkaProducerConf(bootstrap_servers=args.bootstrap)
    ks = KafkaStream(conf)

    # parse streams (allow topic or topic:rate)
    raw = [s.strip() for s in args.streams.split(",") if s.strip()]
    streams = []
    for r in raw:
        if ":" in r:
            topic, rate = r.split(":", 1)
            try:
                rate = int(rate)
            except ValueError:
                rate = args.rate
            streams.append((topic, rate))
        else:
            streams.append((r, args.rate))

    ks.run_multistream(streams, duration_minutes=args.duration, event_count=args.rate)


if __name__ == "__main__":
    # when run directly, use docker-friendly defaults
    run_from_cli()