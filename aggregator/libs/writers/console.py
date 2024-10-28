from pyspark.sql import SparkSession, DataFrame
from libs.writers.base import BaseWriter
from typing import Callable

class ConsoleWriter(BaseWriter):
    """
    Write data to console

    Parameters:
    spark (SparkSession): SparkSession object
    db_conf (dict): Database configuration
    checkpoint_dir (str): App checkpoint directory
    batch_interval (str): Batch interval in seconds
    write_method (str): Write method for the Spark Streaming writeStream
    foreach_query (str): SQL query to execute before writing
    """

    def __init__(self, spark: SparkSession, db_conf: dict, checkpoint_dir: str, batch_interval: str = "10 seconds", write_method: str = "complete", foreachQuery: str = None, **kwargs):
        super().__init__(spark, db_conf, checkpoint_dir, batch_interval, write_method, foreachQuery, **kwargs)
    
    def foreach_write(self, df: DataFrame, epoch_id: int, query: str):
        df.createOrReplaceTempView("AGGREGATED")
        new_df = df.sparkSession.sql(query)
        return new_df.write \
            .format("console") \
            .mode("overwrite") \
            .options(**self.db_conf) \
            .save()
    
    def write(self, df):
        if self.foreach_query:
            return df.writeStream \
                .foreachBatch(lambda df, epoch_id: self.foreach_write(df, epoch_id, self.foreach_query)) \
                .outputMode(self.write_method) \
                .trigger(processingTime=self.batch_interval) \
                .option("checkpointLocation", self.checkpoint_dir) \
                .start()

        return df.writeStream \
            .outputMode(self.write_method) \
            .options(**self.db_conf) \
            .option("checkpointLocation", self.checkpoint_dir) \
            .format("console") \
            .start()
