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

# Set up port forwarding from 80 to 8000
echo "🔧 Setting up port forwarding (80 -> 8000)..."
if command -v iptables &> /dev/null; then
    # Install iptables-persistent if not already installed
    if ! command -v netfilter-persistent &> /dev/null && ! dpkg -l | grep -q iptables-persistent; then
        echo "📦 Installing iptables-persistent..."
        sudo apt install -y iptables-persistent
    fi
    
    # Add port forwarding rules if they don't exist
    if ! sudo iptables -t nat -C PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null; then
        echo "➕ Adding PREROUTING rule..."
        sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000
    fi
    
    if ! sudo iptables -t nat -C OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null; then
        echo "➕ Adding OUTPUT rule..."
        sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8000
    fi
    
    # Save iptables rules
    echo "💾 Saving iptables rules..."
    if command -v netfilter-persistent &> /dev/null; then
        sudo netfilter-persistent save 2>/dev/null || true
    else
        sudo mkdir -p /etc/iptables 2>/dev/null || true
        sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null 2>&1 || true
    fi
    
    echo "✅ Port forwarding configured (port 80 -> 8000)"
else
    echo "⚠️  Warning: iptables not found, skipping port forwarding setup"
fi

# Check if we should skip starting Gunicorn (for systemd setup)
# Set SKIP_GUNICORN=1 to skip starting Gunicorn
if [ "${SKIP_GUNICORN:-0}" = "1" ] || [ "${1:-}" = "--no-start" ]; then
    echo "✅ Deployment setup complete"
    echo ""
    echo "To set up systemd service, run:"
    echo "  sudo bash deployment/setup-systemd.sh"
    echo ""
    exit 0
fi

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
echo "ℹ️  Note: Gunicorn is running in foreground mode."
echo "   To run as a systemd service instead, run:"
echo "   sudo bash deployment/setup-systemd.sh"
echo ""

# Run Gunicorn (foreground by default)
gunicorn -w 4 -b 0.0.0.0:8000 'src.app:app'

