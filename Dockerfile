# Use slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

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
COPY video_processor_lite.py video_processor.py
COPY railway_setup.py .
COPY .gitignore .

# Create necessary directories
RUN mkdir -p downloaded_videos youtube_ready

# Run the application
CMD ["sh", "-c", "python railway_setup.py && python tiktok_to_youtube.py"]
