#!/bin/bash
#
# Setup systemd service for Flask application
# This script copies the service file to systemd and configures it
#
# Usage:
#   sudo bash deployment/setup-systemd.sh
#

set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ ERROR: This script must be run as root (use sudo)"
    echo ""
    echo "Please run:"
    echo "  sudo bash deployment/setup-systemd.sh"
    echo ""
    echo "Or if you're already in the deployment directory:"
    echo "  sudo bash setup-systemd.sh"
    exit 1
fi

# Double-check we can write to systemd directory
if [ ! -w "/etc/systemd/system" ]; then
    echo "❌ ERROR: Cannot write to /etc/systemd/system"
    echo "   This script requires root privileges"
    exit 1
fi

# Get project directory (assume script is run from project root or deployment dir)
if [ -f "deployment/skill-test.service" ]; then
    PROJECT_DIR=$(pwd)
    SERVICE_FILE="$PROJECT_DIR/deployment/skill-test.service"
elif [ -f "skill-test.service" ]; then
    PROJECT_DIR=$(pwd)
    SERVICE_FILE="$PROJECT_DIR/skill-test.service"
else
    echo "❌ Error: skill-test.service not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Determine actual project directory (resolve if we're in deployment/)
if [ -d "$PROJECT_DIR/deployment" ]; then
    ACTUAL_PROJECT_DIR="$PROJECT_DIR"
else
    ACTUAL_PROJECT_DIR=$(dirname "$PROJECT_DIR")
fi

# Get Flask secret key from .env file
ENV_FILE="$ACTUAL_PROJECT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  Warning: .env file not found at $ENV_FILE"
    echo "   Using placeholder FLASK_KEY (you should update this)"
    FLASK_KEY="your-flask-secret-key-here"
else
    FLASK_KEY=$(grep "^FLASK_KEY=" "$ENV_FILE" | cut -d '=' -f2- || echo "your-flask-secret-key-here")
    if [ -z "$FLASK_KEY" ] || [ "$FLASK_KEY" = "your-flask-secret-key-here" ]; then
        echo "⚠️  Warning: FLASK_KEY not found in .env file"
        echo "   Using placeholder (you should update this)"
        FLASK_KEY="your-flask-secret-key-here"
    fi
fi

# Service name (without .service extension)
SERVICE_NAME="skill-test"
SERVICE_FILE_DEST="/etc/systemd/system/${SERVICE_NAME}.service"

echo "=========================================="
echo "Setting up systemd service"
echo "=========================================="
echo ""
echo "Project directory: $ACTUAL_PROJECT_DIR"
echo "Service file: $SERVICE_FILE"
echo "Destination: $SERVICE_FILE_DEST"
echo "Service name: $SERVICE_NAME"
echo ""

# Read the service file and replace placeholders
echo "📋 Reading service file..."
TEMP_SERVICE=$(mktemp)
sed "s|/home/ubuntu/Sean-Anthony-Mael|$ACTUAL_PROJECT_DIR|g" "$SERVICE_FILE" > "$TEMP_SERVICE"
sed -i "s|FLASK_KEY=your-flask-secret-key-here|FLASK_KEY=$FLASK_KEY|g" "$TEMP_SERVICE"

# Copy service file to systemd directory
echo "📁 Copying service file to systemd..."
cp "$TEMP_SERVICE" "$SERVICE_FILE_DEST"
chmod 644 "$SERVICE_FILE_DEST"
rm "$TEMP_SERVICE"

echo "✅ Service file installed"
echo ""

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

echo "✅ systemd daemon reloaded"
echo ""

# Stop service if it's already running
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo "⏹️  Stopping existing service..."
    systemctl stop "$SERVICE_NAME"
    echo "✅ Service stopped"
    echo ""
fi

# Enable service to start on boot
echo "🔌 Enabling service to start on boot..."
systemctl enable "$SERVICE_NAME"
echo "✅ Service enabled"
echo ""

# Start the service
echo "🚀 Starting service..."
if systemctl start "$SERVICE_NAME"; then
    echo "✅ Service start command executed"
else
    echo "❌ Service failed to start"
    echo ""
    echo "=========================================="
    echo "Error Details"
    echo "=========================================="
    echo ""
    echo "Service status:"
    systemctl status "$SERVICE_NAME" --no-pager -l || true
    echo ""
    echo "Recent logs:"
    journalctl -u "$SERVICE_NAME" -n 30 --no-pager || true
    echo ""
    echo "Common issues to check:"
    echo "  1. Virtual environment exists: ls -la $ACTUAL_PROJECT_DIR/.venv/bin/gunicorn"
    echo "  2. Application imports: cd $ACTUAL_PROJECT_DIR && PYTHONPATH=\"$ACTUAL_PROJECT_DIR:$ACTUAL_PROJECT_DIR/src\" python3 -c 'from src.app import app'"
    echo "  3. Port 8000 available: sudo netstat -tlnp | grep 8000"
    echo "  4. Permissions: ls -la $ACTUAL_PROJECT_DIR"
    exit 1
fi

# Wait a moment for service to initialize
echo "⏳ Waiting for service to initialize..."
sleep 3

# Check service status
echo "=========================================="
echo "Service Status"
echo "=========================================="
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "✅ Service is running"
else
    echo "❌ Service failed to start or crashed"
    echo ""
    echo "Service status:"
    systemctl status "$SERVICE_NAME" --no-pager -l || true
    echo ""
    echo "Recent logs:"
    journalctl -u "$SERVICE_NAME" -n 30 --no-pager || true
    echo ""
    echo "Common issues to check:"
    echo "  1. Virtual environment exists: ls -la $ACTUAL_PROJECT_DIR/.venv/bin/gunicorn"
    echo "  2. Application imports: cd $ACTUAL_PROJECT_DIR && PYTHONPATH=\"$ACTUAL_PROJECT_DIR:$ACTUAL_PROJECT_DIR/src\" python3 -c 'from src.app import app'"
    echo "  3. Port 8000 available: sudo netstat -tlnp | grep 8000"
    echo "  4. Permissions: ls -la $ACTUAL_PROJECT_DIR"
    exit 1
fi

echo ""
systemctl status "$SERVICE_NAME" --no-pager -l || true

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  Check status:  sudo systemctl status $SERVICE_NAME"
echo "  View logs:     sudo journalctl -u $SERVICE_NAME -f"
echo "  Restart:        sudo systemctl restart $SERVICE_NAME"
echo "  Stop:           sudo systemctl stop $SERVICE_NAME"
echo "  Start:          sudo systemctl start $SERVICE_NAME"
echo ""

