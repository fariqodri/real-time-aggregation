# Visualization Module

This README provides instructions on how to use the module, both with and without Docker. It also includes steps for setting up the module using Poetry.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Usage with Docker Compose](#usage-with-docker-compose)
- [Usage with Docker](#usage-with-docker)
- [Usage without Docker](#usage-without-docker)

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
    docker run --network avrioc_network_default -p 8501:8501 -e MONGO_URI=mongodb://mongo_admin:mongo_password@mongo:27017 -e DATABASE=avrioc module-name
    ```
    Replace `module-name` with the actual name of your module and arguments with the correct data type.


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
    export MONGO_URI=mongodb://mongo_admin:mongo_password@mongo:27017
    export DATABASE=avrioc
    poetry run streamlit run main.py --server.port=8501 --server.address=0.0.0.0
    ```

## Environment Variables

Envar | Data Type | Default | Required | Description
-----|-----------|--------|-----------|-------------
MONGO_URI | string | None | Yes | MongoDB URL to connect
DATABASE | string | None | Yes | Mongo database name where the collections are stored
