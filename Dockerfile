# Use slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Keep Python logs visible in Railway
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements-railway.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-railway.txt

# Copy application files
COPY tiktok_to_youtube.py .
COPY video_processor_railway.py video_processor.py
COPY railway_runtime_setup.py .
COPY config.defaults.json .
COPY .gitignore .

# Create necessary directories
RUN mkdir -p downloaded_videos youtube_ready

# Run the application
CMD ["sh", "-c", "python -u railway_runtime_setup.py && python -u tiktok_to_youtube.py"]
