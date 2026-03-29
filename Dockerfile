# Use Official PyTorch image with CUDA 11.8 support pre-installed!
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# Set Working Directory
WORKDIR /app

# Install system dependencies needed for bitsandbytes and compilation
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pure requirements list mapping without locked Mac Binaries
COPY requirements.txt .

# Upgrade pip and install
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the platform code inside the container!
COPY . .

# Expose FastAPI Port
EXPOSE 8000

# Default command if not overridden in docker-compose
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
