#!/bin/bash

# Simple script to run the Flask app
# Run this after deploy-simple.sh

set -e

echo "Starting Flask application..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./deploy-simple.sh first"
    exit 1
fi

# Activate virtual environment
. .venv/bin/activate

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "your-ec2-ip")

echo "App will be available at: http://${PUBLIC_IP}:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the app
python3 src/app.py

