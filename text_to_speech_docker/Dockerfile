# Use NVIDIA CUDA base image with Python 3.10
#FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu22.04
FROM python:3.10-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive
    #\
    #NVIDIA_VISIBLE_DEVICES=all \
    #NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Install Python and other system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    build-essential \
    libsndfile1 \
    ffmpeg \
    curl \
    unzip \
    libffi-dev \
    libssl-dev \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install pip version 23.0.1
RUN python -m pip install --upgrade pip && pip install pip==23.0.1

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Clone the Piper repository
RUN git clone -q https://github.com/rmcpantoja/piper /usr/local/piper

# Change to Piper source directory
WORKDIR /usr/local/piper/src/python

# Copy and execute the build script for monotonic_align
COPY build_monotonic_align.sh .
RUN chmod +x build_monotonic_align.sh && ./build_monotonic_align.sh

# Change to the python_run directory to install Piper as a Python package
WORKDIR /usr/local/piper/src/python_run

# Install Piper using pip
RUN pip install .

# Return to the /app directory
WORKDIR /app

RUN mkdir characters

# Create directory for voices and copy model files
COPY voices /app/voices
RUN chmod -R 777 /app/voices

# Ensure all necessary directories have full permissions
RUN chmod -R 777 /usr/local/piper /app

# Copy the API code into the container
COPY api.py .

# Expose the API port
EXPOSE 8080

# Install Gunicorn (if not already in requirements.txt)
RUN pip install --no-cache-dir gunicorn

# Everyone is sudo. We trust everyone.
RUN echo "ALL ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set NVIDIA runtime to enforce GPU usage
#ENV NVIDIA_VISIBLE_DEVICES=all \
#    NVIDIA_REQUIRE_CUDA="cuda>=11.7" \
#    NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics

# Define the entrypoint to run the API using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "api:app"]