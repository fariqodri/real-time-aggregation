# Dockerfile
FROM python:3.10.0-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY pyproject.toml .

RUN pip install poetry==1.8.3 && \
    poetry lock && \
    poetry install

# Copy the rest of the app code
COPY . .

# Expose the Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["poetry", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
