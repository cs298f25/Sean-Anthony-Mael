#!/bin/bash

# EC2 User Data Script
# This script runs automatically when the EC2 instance first boots
# Paste this into the "User data" field when launching your EC2 instance

set -e

# Log everything to a file for debugging
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "=========================================="
echo "Starting automated deployment..."
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y

# Install dependencies
echo "🐍 Installing Python, pip, and Git..."
apt-get install -y python3 python3-pip python3-venv git

# Set up project directory
PROJECT_DIR="/home/ubuntu/Sean-Anthony-Mael"
REPO_URL="https://github.com/cs298f25/Sean-Anthony-Mael.git"  # REPLACE WITH YOUR ACTUAL REPO URL

echo "📥 Cloning repository..."
cd /home/ubuntu
sudo -u ubuntu git clone "$REPO_URL" "$PROJECT_DIR" || {
    echo "⚠️  Git clone failed. Make sure REPO_URL is set correctly."
    exit 1
}

# Change ownership
chown -R ubuntu:ubuntu "$PROJECT_DIR"

# Navigate to project directory
cd "$PROJECT_DIR"

# Run deployment steps (without starting Gunicorn)
echo "🚀 Setting up application..."
sudo -u ubuntu bash -c "
cd $PROJECT_DIR
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
FLASK_KEY=\$(python3 -c 'import secrets; print(secrets.token_hex(32))')
echo \"FLASK_KEY=\$FLASK_KEY\" > .env
PYTHONPATH=\"$PROJECT_DIR:$PROJECT_DIR/src\" python3 -c 'from src.app import app; print(\"✅ Application imports successfully\")'
"

# Get Flask secret key from .env file
FLASK_KEY=$(sudo -u ubuntu cat "$PROJECT_DIR/.env" | grep "^FLASK_KEY=" | cut -d '=' -f2-)

# Create systemd service file
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/flask-app.service << EOF
[Unit]
Description=DevOps Quiz Flask Application
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/.venv/bin"
Environment="PYTHONPATH=$PROJECT_DIR:$PROJECT_DIR/src"
Environment="FLASK_KEY=$FLASK_KEY"
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 'src.app:app'
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=flask-app

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# Enable and start the service
echo "✅ Enabling and starting service..."
systemctl enable flask-app
systemctl start flask-app

# Wait a moment and check status
sleep 5
systemctl status flask-app --no-pager || true

# Set up port forwarding from 80 to 8000
echo "🔧 Setting up port forwarding (80 -> 8000)..."
apt-get install -y iptables-persistent

# Add port forwarding rules if they don't exist
if ! iptables -t nat -C PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null; then
    iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000
fi

if ! iptables -t nat -C OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null; then
    iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8000
fi

# Save iptables rules
if command -v netfilter-persistent &> /dev/null; then
    netfilter-persistent save
else
    mkdir -p /etc/iptables 2>/dev/null; then
    iptables-save > /etc/iptables/rules.v4
fi

echo "✅ Port forwarding configured"

echo "=========================================="
echo "Deployment complete!"
echo "Service status:"
systemctl is-active flask-app || echo "Service may still be starting..."
echo "=========================================="
echo "View logs with: sudo journalctl -u flask-app -f"
echo "Check status with: sudo systemctl status flask-app"
echo "=========================================="
echo "App accessible at: http://crevelingsweb.moraviancs.click (no port needed)"
echo "=========================================="

