FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu18.04

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

# Set NVIDIA runtime to enforce GPU usage
ENV NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics

# Install Python build dependencies
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir scikit-build setuptools wheel

# Copy only requirements.txt first to leverage caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the app files into the container
COPY . /app

RUN mkdir /app/characters
RUN chmod -R 777 /app/characters
RUN cp kim_wexler.mp4 /app/characters/kim_wexler.mp4
RUN cp walter_white.mp4 /app/characters/walter_white.mp4

# Ensure necessary directories exist
RUN mkdir -p /app/uploads /app/outputs /app/characters /app/temp

# Everyone is sudo. We trust everyone.
RUN echo "ALL ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "api:app"]