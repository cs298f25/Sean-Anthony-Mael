#!/bin/bash

# Deployment Script
# Sets up Python environment and installs dependencies

set -e

PROJECT_DIR=$(pwd)
VENV_DIR="$PROJECT_DIR/.venv"

echo "🚀 Setting up EC2 instance..."

# Update system
echo "📦 Updating packages..."
sudo apt update

# Install Python and pip
echo "🐍 Installing Python..."
sudo apt install -y python3 python3-pip python3-venv

echo "🚀 Deploying application..."

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
. .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env file..."
    FLASK_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "FLASK_KEY=$FLASK_KEY" > .env
    echo "✅ Created .env file with Flask secret key"
fi

# Test application import
echo "🧪 Testing application..."
# Set PYTHONPATH to include both project root and src directory
PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/src:$PYTHONPATH" python3 -c "from src.app import app; print('✅ Application imports successfully')"

echo "🚀 Starting Gunicorn..."

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found. Run 'bash deployment/deploy.sh' first."
    exit 1
fi

# Activate virtual environment
. "$VENV_DIR/bin/activate"

# Change to project directory
cd "$PROJECT_DIR"

# Set PYTHONPATH and run Gunicorn
export PYTHONPATH="$PROJECT_DIR:$PROJECT_DIR/src"

echo "📁 Project directory: $PROJECT_DIR"
echo "🐍 Python path: $PYTHONPATH"
echo ""

# Run Gunicorn (foreground by default)
gunicorn -w 4 -b 0.0.0.0:8000 'src.app:app'

