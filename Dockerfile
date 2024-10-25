# Use Python 3.12.7-slim as the base image
FROM python:3.12.7-slim

# Install necessary system dependencies, including PostgreSQL development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container
COPY . .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for external access
EXPOSE 5000

# Define environment variable
ENV FLASK_ENV production

# Run the Flask-SocketIO app
CMD ["python", "run.py"]
