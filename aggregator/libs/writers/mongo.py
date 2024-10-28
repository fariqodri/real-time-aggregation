from pyspark.sql import SparkSession, DataFrame
from libs.writers.base import BaseWriter

class MongoWriter(BaseWriter):
    """
    Write data to MongoDB

    Parameters:
    db_conf (dict): MongoDB connection configuration
    checkpoint_dir (str): Checkpoint directory
    batch_interval (str): Batch interval
    id_column (str): Column name to use as the document ID. If not provided, the default MongoDB auto-generated ID will be used.
    write_method (str): Write method (default: "complete")
    """

    def __init__(self, spark: SparkSession, db_conf: dict, checkpoint_dir: str, batch_interval: str = "10 seconds", write_method: str = "complete", foreachQuery: str = None, id_column: str = None, **kwargs):
        super().__init__(spark, db_conf, checkpoint_dir, batch_interval, write_method, foreachQuery, **kwargs)
        self.id_column = id_column

    def foreach_write(self, df: DataFrame, epoch_id: int, query: str):
        df.createOrReplaceTempView("AGGREGATED")
        new_df = df.sparkSession.sql(query)
        return new_df.write \
            .format("mongodb") \
            .mode("overwrite") \
            .options(**self.db_conf) \
            .save()
    
    def write(self, df):
        if self.id_column and "_id" not in df.columns:
            df = df.withColumnRenamed(self.id_column, "_id")
        
        if self.foreach_query:
            return df.writeStream \
                .foreachBatch(lambda df, epoch_id: self.foreach_write(df, epoch_id, self.foreach_query)) \
                .outputMode(self.write_method) \
                .trigger(processingTime=self.batch_interval) \
                .option("checkpointLocation", self.checkpoint_dir) \
                .start()
        
        df_writer = df.writeStream \
            .outputMode(self.write_method) \
            .options(**self.db_conf) \
            .option("checkpointLocation", self.checkpoint_dir) \
            .format("mongodb") \
            .trigger(processingTime=self.batch_interval)

        return df_writer.start()
