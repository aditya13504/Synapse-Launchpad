FROM nvidia/merlin-tensorflow:23.08

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directories
RUN mkdir -p /data/feature_store /app/models

# Copy source code
COPY . .

# Expose ports for gRPC and REST
EXPOSE 8000 50051

# Start both gRPC and REST servers
CMD ["python", "main.py"]