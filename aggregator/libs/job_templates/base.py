from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import get_json_object, to_timestamp
from pyspark import SparkFiles
from libs.utils.common import parse_conf
from libs.writers import ConsoleWriter
from libs.program_args.base import args_parser
import os

class BaseAggregatorJob:
    """
    Base class for aggregation jobs with console sink

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
    allow_late_for (str): Allow late data for the watermark
    """
    default_json_fields_map = {
        "timestamp": "$.timestamp",
    }

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
            allow_late_for: str = "20 minutes",
            **kwargs
        ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.batch_interval = batch_interval
        self.spark_conf = spark_conf
        self.kafka_conf = kafka_conf
        self.writer_conf = writer_conf
        self.checkpoint_dir = checkpoint_dir
        self.sql_file = sql_file
        self.json_fields_map = {**self.default_json_fields_map, **json_fields_map}
        self.write_method = write_method
        self.allow_late_for = allow_late_for
    
    @property
    def sql_file_name(self):
        return os.path.basename(self.sql_file)

    @property
    def app_checkpoint_dir(self):
        return os.path.join(self.checkpoint_dir, str(hash(self.whole_sql_query)))
    
    @property
    def whole_sql_query(self):
        with open(SparkFiles.get(self.sql_file_name), "r") as f:
            return f.read()
    
    @property
    def streaming_sql_query(self):
        with open(SparkFiles.get(self.sql_file_name), "r") as f:
            query = f.read()
        
        if query.find("-- for_each_batch") == -1 and query.find("-- end_for") == -1:
            return query

        return query.split("-- for_each_batch")[0].strip()

    @property
    def foreach_sql_query(self):
        with open(SparkFiles.get(self.sql_file_name), "r") as f:
            query = f.read()
        
        if query.find("-- for_each_batch") == -1 and query.find("-- end_for") == -1:
            return None

        return query.split("-- for_each_batch")[1].split("-- end_for")[0].strip()
    
    def get_spark_session(self):
        if getattr(self, "spark", None) and isinstance(self.spark, SparkSession):
            return self.spark
        
        builder = SparkSession.builder
        for k, v in self.spark_conf.items():
            builder.config(key=k, value=v)
        builder.config("spark.master", "local[1]")
        sql_name = os.path.basename(self.sql_file)
        spark: SparkSession = builder.appName(sql_name).getOrCreate()
        spark.sparkContext.addFile(self.sql_file)
        self.spark = spark
        return spark

    def get_parsed_df(self) -> DataFrame:
        df = (
            self.get_spark_session()
                .readStream
                .format("kafka")
                .option("kafka.bootstrap.servers", self.bootstrap_servers)
                .option("subscribe", self.topic)
                .options(**self.kafka_conf)
                .load()
        )
        print("JSON field map:", self.json_fields_map)
        select_columns = [
            get_json_object("raw_value", path).alias(alias) for alias, path in self.json_fields_map.items()
        ]
        df = df \
            .selectExpr("CAST(value AS STRING) as raw_value") \
            .select(
                *select_columns
            ) \
            .withColumn("timestamp", to_timestamp("timestamp")) \
            .withWatermark("timestamp", self.allow_late_for)
        return df
    
    def get_aggregated_df(self) -> DataFrame:
        df = self.get_parsed_df()
        df.createOrReplaceTempView("SOURCE")
        query = self.streaming_sql_query
        agg_df = self.get_spark_session().sql(query)
        return agg_df
    
    def write_to_db(self, df: DataFrame):
        writer = ConsoleWriter(
            spark=self.get_spark_session(),
            db_conf=self.writer_conf, 
            checkpoint_dir=self.app_checkpoint_dir, 
            batch_interval=self.batch_interval, 
            write_method=self.write_method,
            foreachQuery=self.foreach_sql_query
        )
        return writer.write(df)
        
    def run(self):
        df = self.get_aggregated_df()
        streaming_query = self.write_to_db(df)
        streaming_query.awaitTermination()
    