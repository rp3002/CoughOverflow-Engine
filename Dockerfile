# Use Ubuntu 24.04 as the base image
FROM ubuntu:24.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    python3 \
    python3-pip \
    steghide \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy sample images folder
COPY sample_images/ sample_images/

# Copy all project files into the container
COPY . /app/

# Download OverflowEngine binary AFTER copying files
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        wget https://github.com/CSSE6400/CoughOverflow-Engine/releases/download/v1.0/overflowengine-amd64 -O overflowengine; \
    else \
        wget https://github.com/CSSE6400/CoughOverflow-Engine/releases/download/v1.0/overflowengine-arm64 -O overflowengine; \
    fi && \
    chmod +x overflowengine

# Download labs.csv
RUN wget https://csse6400.uqcloud.net/resources/labs.csv -O labs.csv

# Install Python dependencies
RUN pip3 install -r requirements.txt --break-system-packages

# Create required runtime directories
RUN mkdir -p sample_images results

# Set environment variables for Flask
ENV FLASK_APP=__init__:create_app
ENV FLASK_RUN_PORT=8080

# Expose Flask port
EXPOSE 8080

# Run the Flask server
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]

