# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies including full ffmpeg (with drawtext/libfreetype)
RUN apt-get update && apt-get install -y \
    ffmpeg \
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

# Pre-download DeepFace gender model weights (~537MB) so cold starts are instant.
# Non-fatal: if the download fails at build time the runtime will download on first use.
RUN python -c "\
import os; \
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'; \
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'; \
import numpy as np; \
from deepface import DeepFace; \
img = np.zeros((224, 224, 3), dtype=np.uint8); \
DeepFace.analyze(img, actions=['gender'], enforce_detection=False, silent=True, detector_backend='opencv'); \
print('DeepFace gender model cached')" || echo "DeepFace pre-download skipped (non-fatal)"

# Copy application code
COPY . .

# Run the setup script then the main script
CMD ["sh", "-c", "python railway_runtime_setup.py && python all_platforms_youtube.py"]
