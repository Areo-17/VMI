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
        group_id='transportation-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        consumer_timeout_ms= 5000,
        enable_auto_commit=True
    )

    logger.info('Connected to topic transportation-stats.')

    try:
        for message in consumer:
            event = message.value
            logger.info(f"Event: {event}")
            records.append(event)

            df = pd.DataFrame(records)
            df.to_csv(f"{OUTPUT_PATH}/transportation.csv", index=False)
    
    except StopIteration:
        print("No messages received in the last 5 seconds. Shutting down the consumer.")

    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
        df = pd.DataFrame(records)
        df.to_csv(f"{OUTPUT_PATH}/transportation.csv", index=False)

    finally:
        logger.info(f"CSV saved to: {OUTPUT_PATH}")
        consumer.close()

if __name__ == "__main__":
    consumer_kafka()