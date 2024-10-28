ARG PY_VERSION=3.10.0

FROM python:${PY_VERSION}-slim-bullseye

ENV POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml .

RUN pip install poetry==1.8.3 && \
    poetry lock && \
    poetry install

COPY generator.py .

ENTRYPOINT ["poetry", "run", "python", "-m", "generator"]
