FROM python:3.10-slim

# Install system dependencies including Node.js and OpenCV requirements
RUN apt-get update && apt-get install -y curl libgl1-mesa-glx libglib2.0-0 && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Build React Frontend
RUN cd frontend && npm install && npm run build

# Default PORT for Render if not provided
ENV PORT=10000
EXPOSE $PORT

# Start FastAPI server
CMD ["python", "server/main.py"]
