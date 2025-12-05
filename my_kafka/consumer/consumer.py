from kafka import KafkaConsumer
import logging
import json
import pandas as pd
import os

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use environment variable if provided; otherwise default to Airflow shared data folder
OUTPUT_PATH = os.environ.get('TRANSPORT_OUTPUT_PATH') or os.path.join(
    os.environ.get('AIRFLOW_HOME', '/opt/airflow'), 'data'
)

def consumer_kafka():
    records = []

    # Try to connect to Kafka; if it fails, create an empty CSV so downstream
    # transform doesn't fail with FileNotFoundError.
    out_file = os.path.join(OUTPUT_PATH, 'transportation.csv')

    # Ensure the destination directory exists
    try:
        os.makedirs(OUTPUT_PATH, exist_ok=True)
    except Exception as e:
        logger.warning(f"Could not create output directory {OUTPUT_PATH}: {e}")

    try:
        consumer = KafkaConsumer(
            'transportation-stats',
            bootstrap_servers=['kafka:9092'],
            group_id='transportation-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            consumer_timeout_ms=30000,
            enable_auto_commit=True
        )

        logger.info('Connected to topic transportation-stats.')

    except Exception as e:
        logger.warning(f"Could not instantiate KafkaConsumer: {e}. Creating empty CSV at {out_file} and returning.")
        # Create empty dataframe file so downstream tasks have something to read
        pd.DataFrame(records).to_csv(out_file, index=False, encoding='utf-8')
        logger.info(f"Wrote 0 records to {out_file}")
        return out_file

    try:
        for message in consumer:
            event = message.value
            logger.info(f"Event: {event}")
            records.append(event)

            df = pd.DataFrame(records)
            df.to_csv(out_file, index=False, encoding='utf-8')
            logger.info(f"Wrote {len(records)} records to {out_file}")

    except StopIteration:
        logger.info("No messages received in the last 30 seconds. Shutting down the consumer.")

    except KeyboardInterrupt:
        logger.info("Stopping consumer...")

    finally:
        # Ensure file is written even if loop exits with no messages
        try:
            pd.DataFrame(records).to_csv(out_file, index=False, encoding='utf-8')
            logger.info(f"Final write: Wrote {len(records)} records to {out_file}")
        except Exception as e:
            logger.warning(f"Failed writing CSV to {out_file}: {e}")

        logger.info(f"CSV saved to: {OUTPUT_PATH}")
        try:
            consumer.close()
        except Exception:
            pass

    return out_file


if __name__ == "__main__":
    # Running this module directly will attempt to consume and always produce the CSV file
    path = consumer_kafka()
    print(f"consumer finished, file: {path}")