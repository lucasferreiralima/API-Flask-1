# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP wsgi.py

# Set work directory
WORKDIR /code

# Install system dependencies (needed for wait-for-it or database clients)
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /code/

# Give execution permission to boot script
RUN chmod +x boot.sh

# Expose port
EXPOSE 5000

# Execute boot script as entry point
ENTRYPOINT ["./boot.sh"]
