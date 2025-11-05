FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including CUDA compatibility libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch with CUDA support first (using PyTorch index)
RUN pip install --no-cache-dir torch==2.2.0+cu121 --index-url https://download.pytorch.org/whl/cu121

# Copy and install remaining requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
