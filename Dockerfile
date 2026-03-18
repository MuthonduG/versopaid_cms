# Dockerfile
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies including networking tools
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    postgresql-client \
    netcat-openbsd \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . /app/

# Create a non-root user to run the app
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Make the wait script executable
COPY wait-for-it.sh /app/django.sh
RUN chmod +x /app/django.sh

USER appuser

# Run the application (will be overridden by docker-compose command)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]