# Use Ubuntu 24.04 as the base image
FROM ubuntu:24.04

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    steghide \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application source files
COPY sample_images/ sample_images/
COPY models/ models/
COPY results/ results/
#COPY labs.csv labs.csv
COPY requirements.txt requirements.txt
COPY __init__.py __init__.py
COPY routes.py routes.py
COPY utils.py utils.py
COPY celery_worker.py celery_worker.py
RUN chmod +x celery_worker.py

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
RUN pip3 install --break-system-packages -r requirements.txt

# Flask environment config
ENV FLASK_APP=__init__:create_app
ENV FLASK_RUN_PORT=8080

# Expose Flask app port
EXPOSE 8080

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]

