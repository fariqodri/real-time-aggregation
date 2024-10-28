import argparse
import os

args_parser = argparse.ArgumentParser(description="Data aggregator")
args_parser.add_argument("--bootstrap-servers", type=str, default=os.getenv("BOOTSTRAP_SERVERS", "localhost:9092"), help="Kafka bootstrap servers")
args_parser.add_argument("--topic", type=str, default=os.getenv("TOPIC", "user.interactions"), help="Kafka topic to read data from")
args_parser.add_argument("--batch-interval", type=str, default=os.getenv("BATCH_INTERVAL", "5 seconds"), help="Batch interval. Example: '10 seconds'")
args_parser.add_argument("--spark-conf", default=[], metavar="KEY=VALUE", nargs='+')
args_parser.add_argument("--kafka-conf", default=[], metavar="KEY=VALUE", nargs='+')
args_parser.add_argument("--writer-conf", default=[], metavar="KEY=VALUE", nargs='+')
args_parser.add_argument("--checkpoint-dir", type=str, default=os.getenv("CHECKPOINT_DIR", "/tmp/checkpoint"), help="Checkpoint directory")
args_parser.add_argument("--json-fields-map", metavar="KEY=VALUE", nargs='+', required=True, help="JSON fields map")
args_parser.add_argument("--sql-file", type=str, default=os.getenv("SQL_FILE"), required=True, help="SQL file path")
args_parser.add_argument("--allow-late-for", type=str, default=os.getenv("ALLOW_LATE", "20 minutes"), help="Late data threshold. If any data arrives later than this threshold, it will be dropped")
args_parser.add_argument("--write-method", type=str, default=os.getenv("WRITE_METHOD", "complete"), help="Write method (default: 'complete')")
