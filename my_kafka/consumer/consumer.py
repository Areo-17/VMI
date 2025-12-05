from kafka import KafkaConsumer
import logging
import json
import pandas as pd
import os

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use environment variable if provided; otherwise default to Airflow plugins data folder
OUTPUT_PATH = os.environ.get('TRANSPORT_OUTPUT_PATH') or os.path.join(
    os.environ.get('AIRFLOW_HOME', '/opt/airflow'), 'plugins', 'data'
)

def consumer_kafka():
    records = []

    consumer = KafkaConsumer(
        'transportation-stats',
        bootstrap_servers=['kafka:29092'],
        group_id='transportation-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        consumer_timeout_ms=30000,
        enable_auto_commit=True
    )

    logger.info('Connected to topic transportation-stats.')

    # Ensure the destination directory exists
    try:
        os.makedirs(OUTPUT_PATH, exist_ok=True)
    except Exception as e:
        logger.warning(f"Could not create output directory {OUTPUT_PATH}: {e}")

    try:
        for message in consumer:
            event = message.value
            logger.info(f"Event: {event}")
            records.append(event)

            df = pd.DataFrame(records)
            out_file = os.path.join(OUTPUT_PATH, 'transportation.csv')
            df.to_csv(out_file, index=False, encoding='utf-8')
            logger.info(f"Wrote {len(records)} records to {out_file}")

    except StopIteration:
        logger.info("No messages received in the last 5 seconds. Shutting down the consumer.")

    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
        df = pd.DataFrame(records)
        out_file = os.path.join(OUTPUT_PATH, 'transportation.csv')
        df.to_csv(out_file, index=False, encoding='utf-8')
        logger.info(f"Wrote {len(records)} records to {out_file}")

    finally:
        logger.info(f"CSV saved to: {OUTPUT_PATH}")
        consumer.close()


if __name__ == "__main__":
    consumer_kafka()