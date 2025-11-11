#!/bin/bash

# Simple EC2 Deployment Script
# Run this from your project root directory after setting up .env

set -e  # Exit on error

echo "=== Simple EC2 Deployment Script ==="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with your API keys first."
    exit 1
fi

echo "✓ .env file found"
echo ""

# Check if we're in the right directory (has src/app.py and frontend/)
if [ ! -f "src/app.py" ] || [ ! -d "frontend" ]; then
    echo "ERROR: Please run this script from the project root directory"
    echo "Expected files: src/app.py and frontend/ directory"
    exit 1
fi

echo "✓ Project structure looks good"
echo ""

# Update system packages
echo "Step 1: Updating system packages..."
sudo apt update -y > /dev/null 2>&1
echo "✓ System updated"
echo ""

# Check and install Python
echo "Step 2: Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    sudo apt install -y python3 python3-pip python3-venv > /dev/null 2>&1
fi
echo "✓ Python $(python3 --version) is installed"
echo ""

# Check and install Node.js
echo "Step 3: Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null 2>&1
    sudo apt install -y nodejs > /dev/null 2>&1
fi
echo "✓ Node.js $(node --version) is installed"
echo ""

# Setup Python virtual environment
echo "Step 4: Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

. .venv/bin/activate
pip install --upgrade pip --quiet
echo "✓ Virtual environment activated"
echo ""

# Install Python dependencies
echo "Step 5: Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Python dependencies installed"
echo ""

# Build frontend
echo "Step 6: Building frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install --silent
fi

echo "Building production bundle..."
npm run build --silent

cd ..
echo "✓ Frontend built successfully"
echo ""

# Check if frontend/dist exists
if [ ! -d "frontend/dist" ] || [ -z "$(ls -A frontend/dist)" ]; then
    echo "WARNING: frontend/dist is empty or doesn't exist"
    echo "The app may not work correctly"
else
    echo "✓ Frontend build verified"
fi
echo ""

# Get EC2 public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")

echo "=== Deployment Complete! ==="
echo ""
echo "Your app is ready to run!"
echo ""
echo "To start the app, run:"
echo "  source .venv/bin/activate"
echo "  python3 src/app.py"
echo ""
echo "Then access it at:"
echo "  http://${PUBLIC_IP}:8000"
echo ""
echo "Make sure your Security Group allows:"
echo "  - Port 8000 (Custom TCP) from 0.0.0.0/0"
echo ""
echo "You can also run the app with the run-app.sh script:"
echo "  sh run-app.sh"
echo ""

