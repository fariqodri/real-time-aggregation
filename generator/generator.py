import time
import random
import os
import argparse
import json
from datetime import datetime
from tempfile import NamedTemporaryFile

from kafka import KafkaProducer

def parse_producer_conf(conf):
    return dict(map(lambda s: s.split('='), conf))

class JSONDataGenerator:
    """
    Generates JSON data points with the following schema:
    {
        "user_id": int,
        "item_id": int,
        "interaction_type": str,
        "timestamp": str
    }
    Parameters:
    data_count (int): Number of data points to generate
    batch_size (int): Number of data points in each batch
    interval_seconds (float): Interval between data points
    user_id_max (int): Maximum user ID
    item_id_max (int): Maximum item ID
    """
    def __init__(self, data_count: int, batch_size: int, interval_seconds: float, user_id_max: int, item_id_max) -> None:
        self.data_count = data_count
        self.batch_size = batch_size
        self.interval_seconds = interval_seconds
        self.user_id_max = user_id_max
        self.item_id_max = item_id_max
        self.file_names = []
    
    def generate_data_point(self):
        return {
            "user_id": random.randint(1, self.user_id_max),
            "item_id": random.randint(1, self.item_id_max),
            "interaction_type": random.choice(["click", "view", "purchase"]),
            "timestamp": datetime.now().isoformat(),
        }
    
    def generate_batches(self) -> list[str] :
        file_names = []
        for i in range(0, self.data_count, self.batch_size):
            with NamedTemporaryFile(mode="w", delete=False) as f:    
                for j in range(min(self.batch_size, self.data_count - i)): 
                    data_point = self.generate_data_point()
                    f.write(json.dumps(data_point) + "\n")
                f.flush()
                file_names.append(f.name)
        return file_names
    
    def generate_data(self):
        self.file_names = self.generate_batches()
        for file_name in self.file_names:
            with open(file_name, "r") as f:
                for line in f:
                    yield line
            time.sleep(self.interval_seconds)
        yield None
    
    def cleanup(self):
        for file_name in self.file_names:
            os.remove(file_name)

class DataSender:
    """
    Sends data to a Kafka topic
    
    Parameters:
    bootstrap_servers (str): Kafka bootstrap servers
    topic (str): Kafka topic to send data to
    producer_conf (dict): Kafka producer configuration
    """
    def __init__(self, bootstrap_servers, topic, producer_conf):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer_conf = producer_conf
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers, **producer_conf)    
    
    def send_batch(self, topic, batch):
        for data_point in batch:
            self.producer.send(topic, data_point.encode())
        self.producer.flush()
    
    def send_single(self, topic, single: str):
        if isinstance(single, dict):
            single = json.dumps(single)
            
        self.producer.send(topic, single.encode())
        self.producer.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data generator")
    parser.add_argument("--data-count", type=int, default=int(os.getenv("DATA_COUNT", 1000)), help="Number of data points to generate")
    parser.add_argument("--interval-seconds", type=float, default=float(os.getenv("INTERVAL_SECONDS", 1.0)), help="Interval between data points")
    parser.add_argument("--batch-size", type=int, default=int(os.getenv("BATCH_SIZE", 100)), help="Number of data points in each batch")
    parser.add_argument("--bootstrap-servers", type=str, default=os.getenv("BOOTSTRAP_SERVERS", "localhost:9092"), help="Kafka bootstrap servers")
    parser.add_argument("--topic", type=str, default=os.getenv("TOPIC", "user.interactions"), help="Kafka topic to send data to")
    parser.add_argument("--producer-conf", default=[], metavar="KEY=VALUE", nargs='+')
    parser.add_argument("--user-id-max", type=int, default=int(os.getenv("MAX_USER_ID", 50)), help="Maximum user ID")
    parser.add_argument("--item-id-max", type=int, default=int(os.getenv("MAX_ITEM_ID", 10)), help="Maximum item ID")

    args = parser.parse_args()
    print("Bootstrap servers", args.bootstrap_servers)
    sender = DataSender(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        producer_conf=parse_producer_conf(args.producer_conf)
    )
    generator = JSONDataGenerator(
        data_count=args.data_count,
        batch_size=args.batch_size,
        interval_seconds=args.interval_seconds,
        user_id_max=args.user_id_max,
        item_id_max=args.item_id_max
    )
    for data in generator.generate_data():
        if data is None:
            break
        sender.send_single(args.topic, data)
    
    generator.cleanup()
