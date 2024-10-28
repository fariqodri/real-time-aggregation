ARG PY_VERSION=3.10.0
ARG SPARK_VERSION=3.5.1

FROM python:${PY_VERSION} AS base

ENV POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml ./

RUN apt-get update && apt-get install -y zip

RUN pip install poetry==1.8.3 && \
    poetry lock && \
    poetry export -o requirements.txt -vv --without dev && \
    pip install -r requirements.txt -t deps && \
    touch deps/.placeholder && \
    cd deps && zip -r ../deps.zip .

COPY . .

RUN zip -r libs.zip libs


FROM apache/spark:${SPARK_VERSION}-python3

COPY --from=base --chown=spark:spark /app/*.zip /app/jobs ./
COPY --from=base --chown=spark:spark /app/ .

USER root

VOLUME [ "/ivy" ]

ENTRYPOINT [ \
    "/opt/spark/bin/spark-submit", \
    "--packages", \
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.4.0", \
    "--conf", \
    "spark.driver.extraJavaOptions=-Divy.cache.dir=/tmp/ivy -Divy.home=/tmp/ivy", \
    "--py-files", \
    "deps.zip,libs.zip" \
]
