# Generator Module

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
    ```

### Usage with Docker

To use this module with Docker, follow these steps:

1. Install Docker on your machine if you haven't already.
2. Run the `docker-compose-infra.yaml` in the root directory by running
    ```shell
    docker-compose -f docker-compose-infra.yaml up -d
    ```

3. Build the Docker image by running the following command in the terminal:
    ```shell
    docker build -t module-name .
    ```
3. Run the Docker container using the following example command:
    ```shell
    docker run -e BOOTSTRAP_SERVERS=kafka:9092 -e TOPIC=user.interactions -e DATA_COUNT=<int> -e BATCH_SIZE=<int> -e INTERVAL_SECONDS=<int> -e MAX_USER_ID=<int> -e MAX_ITEM_ID=<int> module-name --producer-conf key=value key=value
    ```
    Replace `module-name` with the actual name of your module and arguments with the correct data type. The container will exit as soon as all data are published.


### Usage without Docker

To use this module without Docker, follow these steps:

1. Install Poetry on your machine if you haven't already. Recommended to use 1.8.3
2. Install Python on your machine if you haven't already. The only version of Python this module has been tested with in Python 3.10.0
3. If you want to use your own Kafka, you may need to install it before running this program. Otherwise, you can use the one provided in `docker-compose-infra.yaml`.
4. Run this commands:
    ```shell
    poetry env use $(which python3)
    poetry shell
    poetry install
    ```
5. Run the program with this command:
    ```shell
    poetry run python -m generator --bootstrap-server localhost:29092 --topic user.interactions --data-count <int> --batch-size <int> --interval-seconds <int> --user-id-max <int> --item-id-max <int> --producter-conf key=value key=value
    ```

## Program Arguments

Flag | Data Type | Default | Required | Description
-----|-----------|--------|-----------|-------------
--data-count | int | 1000 | No | Number of data points to be generated
--interval-seconds | float | 1 | No |  Pause (in seconds) between batches
--batch-size | int | 100 | No |  Number of data points for each batch
--bootstrap-servers | string | localhost:9092 | Yes | Comma-separated Kafka bootstrap servers to send the data
--topic | string | user.interactions | Yes | Kafka topic
--producer-conf | string key-values | None | No | Kafka producer configs
--user-id-max | int | 50 | No | Maximum value of user_id
--item-id-max | int | 10 | No | Maximum value of item_id
