#!/bin/bash

# Stop PostgreSQL
echo "Ping PostgreSQL..."
sudo systemctl stop postgresql
echo "PostgreSQL stopped successfully!"

# Remove all stopped Docker containers
echo "Removing all stopped Docker containers..."
sudo docker rm -f $(sudo docker ps -aq)
echo "All stopped Docker containers removed!"

# Start Docker containers using Docker Compose
echo "Starting Docker containers..."
sudo docker-compose up -d
echo "Docker containers started successfully!"

