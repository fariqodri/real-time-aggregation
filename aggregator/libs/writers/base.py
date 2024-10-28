from pyspark.sql import DataFrame, DataFrameWriter
from pyspark.sql.streaming.query import StreamingQuery
from pyspark.sql import SparkSession
from typing import Callable

class BaseWriter:
    """
    Base class for data sink for Spark Streaming

    Parameters:
    spark (SparkSession): SparkSession object
    db_conf (dict): Database configuration
    checkpoint_dir (str): App checkpoint directory
    batch_interval (str): Batch interval in seconds
    write_method (str): Write method for the Spark Streaming writeStream
    foreach_query (str): SQL query to execute before writing
    """
    def __init__(
            self,
            spark: SparkSession,
            db_conf: dict,
            checkpoint_dir: str,
            batch_interval: str = "10 seconds",
            write_method: str = "complete", 
            foreach_query: str = None,
            **kwargs
        ):
        self.spark = spark
        self.db_conf = db_conf
        self.checkpoint_dir = checkpoint_dir
        self.batch_interval = batch_interval
        self.write_method = write_method
        self.foreach_query = foreach_query
    
    def foreach_write(self, df: DataFrame, epoch_id: int, query: str):
        raise NotImplementedError

    def write(self, df: DataFrame) -> StreamingQuery:
        raise NotImplementedError
