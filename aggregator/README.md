# Aggregator Module

This README provides instructions on how to use the module, both with and without Docker. It also includes steps for setting up the module using Poetry.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Usage with Docker Compose](#usage-with-docker-compose)
- [Usage with Docker](#usage-with-docker)
- [Usage without Docker](#usage-without-docker)
- [Program Arguments](#program-arguments)

## Prerequisites

- Python 3.10.0
- Docker
- Poetry for dependency management

## Running The Program

### Usage with Docker Compose

This is the easiest way to run this program. Follow these steps:
1. Install Docker and Docker Compose on your machine if you haven't already.
2. Run this command:
    ```shell
    docker-compose -f docker-compose-infra.yaml -f docker-compose-app.yaml up -d
    docker-compose -f docker-compose-streaming.yaml up <service-name1> <service-name2> --build
    ```
    You can run the `up` command without providing any service-name, which will run all of the aggregation jobs at once. Only do this if you have enough CPU and memory locally. Each service name runs its own assigned aggregation SQL query listed below. The explanation of each SQL query is written in the SQL file.

| Service Name | Aggregation SQL File | Mongo Table
|--------------|----------------------|--------------|
| agg_avg_per_item_5m | [sql_files/avg_interactions_per_item_5m.sql](sql_files/avg_interactions_per_item_5m.sql) | avg_interactions_per_item_5m
| agg_avg_per_item_whole | [sql_files/avg_interactions_per_item_whole.sql](sql_files/avg_interactions_per_item_whole.sql) | avg_interactions_per_item_whole
| agg_avg_per_user_5m | [sql_files/avg_interactions_per_user_5m.sql](sql_files/avg_interactions_per_user_5m.sql) | avg_interactions_per_user_5m
| agg_avg_per_user_whole | [sql_files/avg_interactions_per_user_whole.sql](sql_files/avg_interactions_per_user_whole.sql) | avg_interactions_per_user_whole
| agg_interactions_per_item_5m | [sql_files/interactions_per_item_5m.sql](sql_files/interactions_per_item_5m.sql) | interactions_per_item_5m
| agg_interactions_per_user_5m | [sql_files/interactions_per_user_5m.sql](sql_files/interactions_per_user_5m.sql) | interactions_per_user_5m
| agg_max_min_per_item | [sql_files/max_min_per_item.sql](sql_files/max_min_per_item.sql) | max_min_per_item

### Usage with Docker

To use this module with Docker, follow these steps:

1. Install Docker on your machine if you haven't already.
2. Run the `docker-compose-infra.yaml` in the root directory by running
    ```shell
    docker-compose -f docker-compose-infra.yaml up -d
    ```

3. Build the Docker image by running the following command in the terminal:
    ```shell
    docker build -f Dockerfile -t <module-name> .
    ```
3. Run the Docker container using the following example command:
    ```shell
    docker run -v /tmp/ivy:/tmp/ivy -v /tmp/checkpoint:/tmp/checkpoint --network avrioc_network_default <module-name> mongo.py --bootstrap-servers kafka:9092 --topic user.interactions --batch-interval "5 seconds" --kafka-conf startingOffsets=earliest --checkpoint-dir /tmp/checkpoint --json-fields-map "user_id=$.user_id" "item_id=$.item_id" "interaction_type=$.interaction_type" --sql-file sql_files/<aggregation-to-run>.sql --writer-conf spark.mongodb.connection.uri=mongodb://mongo_admin:mongo_password@mongo:27017 spark.mongodb.database=avrioc spark.mongodb.collection=<mongo-collection>
    ```
    Replace `module-name` with the actual name of your module and arguments with the correct data type.


### Usage without Docker

To use this module without Docker, follow these steps:

1. Install Poetry on your machine if you haven't already. Recommended to use 1.8.3
2. Install Python on your machine if you haven't already. The only version of Python this module has been tested with in Python 3.10.0
3. Install Spark 3.5.0 through this [link](https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz)
4. Install Java 11 or 17
5. If you want to use your own Kafka, you may need to install it before running this program. Otherwise, you can use the one provided in `docker-compose-infra.yaml`.
4. Compress pip dependencies and library Python files into zip files.
    ```bash
    poetry export -o requirements.txt -vv --without dev
    pip install -r requirements.txt -t deps
    touch deps/.placeholder
    cd deps && zip -r ../deps.zip * && cd ..
    zip -r libs.zip libs
    ```

5. Run spark-submit command:
    ```shell
    /path/to/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.4.0 --conf "spark.driver.extraJavaOptions=-Divy.cache.dir=/tmp/ivy -Divy.home=/tmp/ivy" --py-files deps.zip,libs.zip jobs/mongo.py --bootstrap-servers kafka:9092 --topic user.interactions --batch-interval "5 seconds" --kafka-conf startingOffsets=earliest --checkpoint-dir /tmp/checkpoint --json-fields-map "user_id=$.user_id" "item_id=$.item_id" "interaction_type=$.interaction_type" --sql-file sql_files/<aggregation-to-run>.sql --writer-conf spark.mongodb.connection.uri=mongodb://mongo_admin:mongo_password@mongo:27017 spark.mongodb.database=avrioc spark.mongodb.collection=<mongo-collection>
    ```

## Program Arguments

Flag | Data Type | Default | Required | Description
-----|-----------|--------|-----------|-------------
--bootstrap-server | string | localhost:9092 | Yes | Kafka bootstrap servers to consume from
--topic | string | user.interactions | Yes | Kafka topic
--batch-interval | string | 5 seconds | No | Interval between micro-batches
--spark-conf | key=value | None | No | Addiitional Spark configurations
--kafka-conf | key=value | None | No | Additional Kafka consumer configuration
--writer-conf | key=value | None | Yes | Mongo write configuration. Check this [page](https://www.mongodb.com/docs/spark-connector/current/streaming-mode/streaming-write-config/) for guidance
--checkpoint-dir | string | /tmp/checkpoint | No | Directory path to store Spark Streaming checkpoint. In real use-case, this should be in HDFS-compatible filesystem.
--json-fields-map | key=value | timestamp=$.timestamp | Yes | JSON path to read the values from and its alias. Key is alias and value is JSON path
--sql-file | string | None | Yes | SQL file that Spark reads to perform real-time aggregation
--allow-late-for | string | 20 mninutes | No | Late data threshold. If any data arrives later than this threshold, it will be dropped
--write-method | string | complete | No | Spark streaming outputMode

## Modifying or Adding Aggregation SQL Files

This module is flexible for you to perform new aggregations. You just need to add/modify the SQL files with this steps:

1. Edit or add new SQL files in the `sql_files` folder. You can look at the few examples as reference. There are 2 built-in tables available for you to use: `SOURCE` and `AGGREGATED`. Further explanation about this is on the next section. 

    Since Spark Streaming doesn't support nested aggregations, if you need to do so, you have to encapsulate the 2nd, 3rd, or Nth aggregations between the `-- for_each_batch` and `-- end_for` signs. Check the example at [max_min_per_item.sql](sql_files/max_min_per_item.sql)

2. Run the same Docker build command in [Usage with Docker](#usage-with-docker) section
3. If you modify any existing SQL files, the application will create a new streaming checkpoint directory. As such, you don't have to delete the checkpoint directory if you want to re-read the Kafka message from the beginning to backfill the data.

## Built-in SOURCE and AGGREGATED Table

There are 2 built-in tables if you're using the aggregation SQL files:

1. SOURCE table: This is the semi-raw table where all the fields from the JSON Kafka message have been parsed into DataFrame columns.
2. AGGREGATED table: This is the result of the first aggregation if you're using `-- for_each_batch`. For example, in this SQL query, AGGREGATED is the result of the "First aggregation" query
    ```sql
    -- First aggregation
    SELECT user_id, COUNT(*) AS interaction_count
    FROM SOURCE
    GROUP BY user_id

    -- for_each_batch
    SELECT '_id' AS _id, AVG(interaction_count) AS avg_interactions_per_user
    FROM AGGREGATED
    -- end_for
    ```

## Design Decisions

1. This module was created with flexibility and extendability in mind. For example, using SQL files for aggregation instead of programmatical PySpark DataFrame libraries makes it easier to add new aggregation tables
2. Changing SQL files and backfilling existing destination table for that aggregation is automatic. This was done by storing the checkpoint in a directory where the directory name is the hash value of the SQL query.
3. This module currently only has 2 destinations: console and mongo. I keep the console destination for ease of debugging. If you want to run the pipeline with console only, replace the `mongo.py` to `console.py` in the pipeline start commands.
