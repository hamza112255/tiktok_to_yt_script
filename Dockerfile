# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies for DeepFace and OpenCV
RUN apt-get update && apt-get install -y \
    libxcb1 \
    libxcb-render0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxext6 \
    libsm6 \
    libice6 \
    libx11-6 \
    libxrender1 \
    libgomp1 \
    libglib2.0-0 \
    fonts-dejavu-core \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the setup script then the main script
CMD ["sh", "-c", "python railway_runtime_setup.py && python all_platforms_youtube.py"]
