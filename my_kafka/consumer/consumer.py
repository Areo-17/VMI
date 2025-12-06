#!/usr/bin/env python3
from kafka import KafkaConsumer
import logging
import json
import pandas as pd
import os

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_PATH = os.environ.get('TRANSPORT_OUTPUT_PATH') or os.path.join(
    os.environ.get('AIRFLOW_HOME', '/opt/airflow'), 'data'
)
try:
    os.makedirs(OUTPUT_PATH, exist_ok=True)
except Exception:
    pass


def consumer_kafka(output_file=None, topics_list=None):
    """
    Kafka consumer capable of:
      ✓ Subscribing to specific topics (via topics_list arg) or env var TOPICS
      ✓ Writing 1 CSV per topic (multi-output mode)
      ✓ Writing a single merged CSV (ELT mode) using `output_file=...`

    :param output_file: If set, writes all consumed records to this single file.
    :param topics_list: List of strings (e.g. ['product-events']). Overrides env var.
    """

    # ----- Load topics -----
    if topics_list:
        topics = topics_list
    else:
        env_topics = os.environ.get("TOPICS")
        if env_topics:
            topics = [t.strip() for t in env_topics.split(",") if t.strip()]
        else:
            topics = ["transportation-stats", "urban-sensors"]

    logger.info(f"Consumer will subscribe to: {topics}")

    # Records grouped by topic
    records_by_topic = {t: [] for t in topics}

    # Ensure destination exists
    try:
        os.makedirs(OUTPUT_PATH, exist_ok=True)
    except Exception as e:
        logger.warning(f"Could not create output directory {OUTPUT_PATH}: {e}")

    try:
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=[os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")],
            group_id=os.environ.get("KAFKA_CONSUMER_GROUP", "transportation-group"),
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            consumer_timeout_ms=int(os.environ.get("CONSUMER_TIMEOUT_MS", 30000)),
            enable_auto_commit=True
        )
        logger.info(f"Connected to Kafka topics: {topics}")

    except Exception as e:
        logger.warning(f"Could not instantiate KafkaConsumer: {e}. Returning empty output.")

        # ELT mode → write empty single file
        if output_file:
            empty_path = os.path.join(OUTPUT_PATH, output_file)
            pd.DataFrame([]).to_csv(empty_path, index=False)
            return empty_path

        return None

    # ----- Message polling -----
    try:
        for message in consumer:
            topic = message.topic
            event = message.value
            logger.info(f"[{topic}] Event: {event}")

            # Append to topic list
            records_by_topic.setdefault(topic, []).append(event)

            # Multi-output mode: write one CSV per topic on every message
            if not output_file:
                out_file = os.path.join(OUTPUT_PATH, f"{topic.replace('/', '_')}.csv")
                try:
                    pd.DataFrame(records_by_topic[topic]).to_csv(out_file, index=False)
                except Exception as e:
                    logger.warning(f"Failed writing CSV for topic {topic}: {e}")

    except StopIteration:
        logger.info("Timeout reached, stopping consumer.")
    except KeyboardInterrupt:
        logger.info("Consumer interrupted manually.")
    finally:
        # FINAL WRITE
        if not output_file:
            # Multi-output mode: write each topic separately
            for t, recs in records_by_topic.items():
                out_file = os.path.join(OUTPUT_PATH, f"{t.replace('/', '_')}.csv")
                pd.DataFrame(recs).to_csv(out_file, index=False)
            
            try:
                consumer.close()
            except Exception:
                pass
            return None

        else:
            # ELT single-output mode: merge all topic records
            all_records = []
            for recs in records_by_topic.values():
                all_records.extend(recs)

            output_path = os.path.join(OUTPUT_PATH, output_file)

            # Create DataFrame and Save
            df = pd.DataFrame(all_records)
            df.to_csv(output_path, index=False)
            logger.info(f"Single-output ELT mode: wrote {len(df)} records → {output_path}")

            try:
                consumer.close()
            except Exception:
                pass

            return output_path

if __name__ == "__main__":
    # Example test run
    path = consumer_kafka(output_file="test_output.csv")
    print(f"consumer finished, file: {path}")