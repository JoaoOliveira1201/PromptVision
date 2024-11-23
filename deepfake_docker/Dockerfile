# Use Ubuntu base image instead of CUDA
FROM ubuntu:18.04

# Set up working directory
WORKDIR /app

# Install system dependencies and build tools
RUN apt-get update && apt-get install -y \
    python3.6 \
    python3-pip \
    python3.6-dev \
    ffmpeg \
    build-essential \
    cmake \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Remove NVIDIA-specific environment variables since we're not using GPU
# ENV NVIDIA_VISIBLE_DEVICES=all \
#     NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics

# Install Python build dependencies
RUN pip3 install --upgrade pip \
    && pip3 install scikit-build setuptools wheel

# Copy only requirements.txt first to leverage caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy the rest of the app files into the container
COPY . /app

# Ensure necessary directories exist
RUN mkdir -p /app/uploads /app/outputs /app/characters /app/temp

# Everyone is sudo. We trust everyone.
RUN echo "ALL ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "api:app"]