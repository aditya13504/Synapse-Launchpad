FROM nvidia/merlin-hugectr:23.08

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create model and data directories
RUN mkdir -p /app/models /app/data /app/notebooks

# Copy source code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start the inference service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]