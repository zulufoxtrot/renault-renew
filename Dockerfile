# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY templates/ templates/
COPY docker/entrypoint.sh .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Create directory for output files and data
RUN mkdir -p /app/output /app/data && \
    chmod -R 777 /app/data /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_PORT=5000
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Run the Flask API via entrypoint
ENTRYPOINT ["./entrypoint.sh"]
