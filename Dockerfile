FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download YOLOv8n weights so container starts instantly
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Copy project files
COPY . .

# Set default port
ENV PORT=8000
EXPOSE 8000

CMD ["python", "main.py"]
