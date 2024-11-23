#!/bin/bash

# Remove all stopped containers
docker container prune -f

# Remove all unused volumes
docker volume prune -f

# Remove all unused networks
docker network prune -f

# Remove all dangling (unused) images
docker image prune -a -f

# Remove all build cache
docker builder prune -a -f
