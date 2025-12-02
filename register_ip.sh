#!/bin/bash
#
# Register EC2 instance public IP with DNS subdomain service
#
# Usage:
#   ./register_ip.sh
#
# The script will:
#   1. Load values from .env file if present
#   2. Prompt for any missing values (username, label, token)
#
# To use a .env file, create a file named .env in the same directory
# with the following format:
#   USERNAME=yourusername
#   LABEL=web
#   TOKEN=your-bearer-token-here
#
# Security: Never commit .env files to version control!

API_URL="https://webapps.cs.moravian.edu/awsdns/"

# Load .env file if it exists
if [ -f .env ]; then
    . .env
fi

# Prompt for values if not set (from .env or otherwise)
if [ -z "$USERNAME" ]; then
    read -p "Enter your username: " USERNAME
fi

if [ -z "$LABEL" ]; then
    read -p "Enter subdomain label (e.g., 'web', 'app', 'db'): " LABEL
fi

if [ -z "$TOKEN" ]; then
    read -p "Enter your bearer token: " TOKEN
fi

# Validate inputs
if [ -z "$USERNAME" ] || [ -z "$TOKEN" ] || [ -z "$LABEL" ]; then
    echo "ERROR: Username, token, and label are all required" >&2
    exit 1
fi

# Check if port forwarding is interfering and temporarily disable it
HAS_PREROUTING=false
HAS_OUTPUT=false
PORT_FORWARDING_DISABLED=false

if sudo iptables -t nat -C PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null; then
    HAS_PREROUTING=true
fi

if sudo iptables -t nat -C OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null; then
    HAS_OUTPUT=true
fi

# Temporarily disable port forwarding if it exists (to allow IP detection)
if [ "$HAS_PREROUTING" = "true" ] || [ "$HAS_OUTPUT" = "true" ]; then
    PORT_FORWARDING_DISABLED=true
    if [ "$HAS_PREROUTING" = "true" ]; then
        sudo iptables -t nat -D PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null || true
    fi
    if [ "$HAS_OUTPUT" = "true" ]; then
        sudo iptables -t nat -D OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null || true
    fi
fi

# Get public IP (try multiple methods to avoid port forwarding issues)
echo "Retrieving public IP address..."
PUBLIC_IP=""

# Try EC2 metadata service first (if on EC2, not affected by port forwarding)
if PUBLIC_IP=$(curl -s --max-time 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null); then
    if [ -n "$PUBLIC_IP" ] && echo "$PUBLIC_IP" | grep -qE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'; then
        echo "Retrieved IP from EC2 metadata service"
    else
        PUBLIC_IP=""
    fi
fi

# Try HTTPS services (not affected by port forwarding)
if [ -z "$PUBLIC_IP" ]; then
    if PUBLIC_IP=$(curl -s --max-time 5 https://checkip.amazonaws.com 2>/dev/null); then
        if [ -n "$PUBLIC_IP" ] && echo "$PUBLIC_IP" | grep -qE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'; then
            echo "Retrieved IP from checkip.amazonaws.com (HTTPS)"
        else
            PUBLIC_IP=""
        fi
    fi
fi

# Try alternative HTTPS service
if [ -z "$PUBLIC_IP" ]; then
    if PUBLIC_IP=$(curl -s --max-time 5 https://api.ipify.org 2>/dev/null); then
        if [ -n "$PUBLIC_IP" ] && echo "$PUBLIC_IP" | grep -qE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'; then
            echo "Retrieved IP from ipify.org (HTTPS)"
        else
            PUBLIC_IP=""
        fi
    fi
fi

# Fallback to HTTP (only works if port forwarding was disabled)
if [ -z "$PUBLIC_IP" ]; then
    if PUBLIC_IP=$(curl -s --max-time 5 http://checkip.amazonaws.com 2>/dev/null); then
        # Clean the IP (remove any HTML/whitespace)
        PUBLIC_IP=$(echo "$PUBLIC_IP" | tr -d '[:space:]' | grep -oE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)
    fi
fi

# Validate IP format
if [ -z "$PUBLIC_IP" ] || ! echo "$PUBLIC_IP" | grep -qE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'; then
    # Re-enable port forwarding before exiting
    if [ "$PORT_FORWARDING_DISABLED" = "true" ]; then
        if [ "$HAS_PREROUTING" = "true" ]; then
            sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null || true
        fi
        if [ "$HAS_OUTPUT" = "true" ]; then
            sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null || true
        fi
    fi
    echo "ERROR: Could not determine public IP address" >&2
    exit 1
fi

echo "Public IP: $PUBLIC_IP"
echo "Registering subdomain: ${USERNAME}${LABEL}..."

# Make API call
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/setip" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$USERNAME\",\"label\":\"$LABEL\",\"ipAddress\":\"$PUBLIC_IP\"}")

# Extract HTTP status code (last line)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
# Extract response body (all but last line)
BODY=$(echo "$RESPONSE" | sed '$d')

# Re-enable port forwarding if it was disabled
if [ "$PORT_FORWARDING_DISABLED" = "true" ]; then
    if [ "$HAS_PREROUTING" = "true" ]; then
        if ! sudo iptables -t nat -C PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null; then
            sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null || true
        fi
    fi
    if [ "$HAS_OUTPUT" = "true" ]; then
        if ! sudo iptables -t nat -C OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null; then
            sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8000 2>/dev/null || true
        fi
    fi
    # Save rules
    if command -v netfilter-persistent &> /dev/null; then
        sudo netfilter-persistent save 2>/dev/null || true
    fi
fi

# Check result
if [ "$HTTP_CODE" -eq 200 ]; then
    echo "SUCCESS: Subdomain ${USERNAME}${LABEL} registered with IP $PUBLIC_IP"
    exit 0
else
    echo "ERROR: Registration failed (HTTP $HTTP_CODE)" >&2
    if [ -n "$BODY" ]; then
        echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    fi
    exit 1
fi
