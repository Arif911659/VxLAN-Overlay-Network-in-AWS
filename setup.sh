#!/bin/bash
set -e  # Exit immediately if a command fails

# Update the system
sudo apt update -y

# Install Docker
sudo apt install -y docker.io

# Start Docker and enable it to run on boot
sudo systemctl start docker
sudo systemctl enable docker

# Create a separate Docker bridge network
sudo docker network create --subnet 172.18.0.0/16 vxlan-net

# List all Docker networks
sudo docker network ls

# Display network interfaces
ip a
