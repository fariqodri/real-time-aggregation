from pyspark.sql import DataFrame
from libs.job_templates.base import BaseAggregatorJob
from libs.writers.mongo import MongoWriter

class MongoAggregatorJob(BaseAggregatorJob):
    """
    Aggregator job with MongoDB sink

    Parameters:
    bootstrap_servers (str): Kafka bootstrap servers
    topic (str): Kafka topic to read data from
    batch_interval (int): Batch interval in seconds
    checkpoint_dir (str): Spark Streaming base checkpoint directory
    sql_file (str): SQL file containing the aggregation query
    json_fields_map (dict): JSON fields map to map JSON fields to DataFrame columns (e.g. {"timestamp": "$.timestamp"})
    spark_conf (dict): Spark configuration
    kafka_conf (dict): Kafka configuration
    writer_conf (dict): Writer configuration
    write_method (str): Write method for the Spark Streaming writeStream
    """
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        batch_interval: int,
        checkpoint_dir: str,
        sql_file: str,
        json_fields_map: dict,
        spark_conf: dict = {},
        kafka_conf: dict = {},
        writer_conf: dict = {},
        write_method: str = "complete",
        **kwargs
    ):
        super().__init__(
            bootstrap_servers,
            topic,
            batch_interval,
            checkpoint_dir,
            sql_file,
            json_fields_map,
            spark_conf,
            kafka_conf,
            writer_conf,
            write_method,
            **kwargs
        )

    def write_to_db(self, df: DataFrame):
        writer = MongoWriter(
            spark=self.get_spark_session(),
            db_conf=self.writer_conf, 
            checkpoint_dir=self.app_checkpoint_dir, 
            batch_interval=self.batch_interval, 
            write_method=self.write_method,
            foreachQuery=self.foreach_sql_query
        )
        return writer.write(df)
