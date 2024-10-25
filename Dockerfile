# Use Python 3.12.7-slim as the base image
FROM python:3.12.7-slim

# Install necessary system dependencies, including PostgreSQL development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variable to avoid Python buffering output
ENV PYTHONUNBUFFERED=1

# Create and set the working directory in the container
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 5000 for external access
EXPOSE 5000

# Define environment variable
ENV NAME World

# Use eventlet as the worker for Flask-SocketIO
CMD ["python", "run.py"]
