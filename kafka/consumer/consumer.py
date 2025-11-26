from kafka import KafkaConsumer
import logging
import json
import pandas as pd
import os

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data"))

def consumer_kafka():
    records = []

    consumer = KafkaConsumer(
        'transportation-stats',
        bootstrap_servers=['localhost:29092'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )

    logger.info('Connected to topic transportation-stats.')

    try:
        for message in consumer:
            event = message.value
            logger.info(f"Event: {event}")
            records.append(event)

            df = pd.DataFrame(records)
            df.to_csv(OUTPUT_PATH, index=False)

    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
        df = pd.DataFrame(records)
        df.to_csv(OUTPUT_PATH, index=False)

    finally:
        logger.info(f"CSV saved to: {OUTPUT_PATH}")
        consumer.close()

if __name__ == "__main__":
    consumer_kafka()