#!/bin/bash

###############################################################################
# Agentify Device Registration Script
# 
# This script registers a Raspberry Pi or Linux device with Agentify
# 
# Usage:
#   ./register-device.sh <CLAIM_TOKEN> <DEVICE_MANAGER_URL>
#
# Example:
#   ./register-device.sh abc123def456 https://device-manager.agentify.ai
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ "$#" -ne 2 ]; then
    echo -e "${RED}Error: Missing arguments${NC}"
    echo "Usage: $0 <CLAIM_TOKEN> <DEVICE_MANAGER_URL>"
    echo "Example: $0 abc123def456 https://device-manager.agentify.ai"
    exit 1
fi

CLAIM_TOKEN=$1
DEVICE_MANAGER_URL=$2

echo -e "${GREEN}=== Agentify Device Registration ===${NC}"
echo ""

# Generate device ID
DEVICE_ID=$(hostname)-$(date +%s)
echo -e "${YELLOW}Device ID:${NC} $DEVICE_ID"

# Get device name (hostname)
DEVICE_NAME=$(hostname)
echo -e "${YELLOW}Device Name:${NC} $DEVICE_NAME"

# Detect device type
if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    DEVICE_TYPE="raspberry_pi"
elif [ -f /etc/os-release ]; then
    DEVICE_TYPE="generic_linux"
else
    DEVICE_TYPE="other"
fi
echo -e "${YELLOW}Device Type:${NC} $DEVICE_TYPE"

# Get Tailscale IP
echo -e "${YELLOW}Getting Tailscale IP...${NC}"
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "")
if [ -z "$TAILSCALE_IP" ]; then
    echo -e "${RED}Error: Tailscale is not running or not configured${NC}"
    echo "Please run: tailscale up --authkey=<YOUR_AUTH_KEY>"
    exit 1
fi
echo -e "${GREEN}Tailscale IP:${NC} $TAILSCALE_IP"

# Get Tailscale hostname
TAILSCALE_HOSTNAME=$(tailscale status --json 2>/dev/null | jq -r '.Self.HostName' || echo "$DEVICE_NAME")
echo -e "${YELLOW}Tailscale Hostname:${NC} $TAILSCALE_HOSTNAME"

# Get Tailscale node ID
TAILSCALE_NODE_ID=$(tailscale status --json 2>/dev/null | jq -r '.Self.ID' || echo "")

# Detect capabilities
echo -e "${YELLOW}Detecting device capabilities...${NC}"

# CPU
CPU_CORES=$(nproc)
CPU_MODEL=$(lscpu | grep "Model name" | cut -d':' -f2 | xargs || echo "Unknown")

# Memory (in MB)
MEMORY_MB=$(free -m | awk '/^Mem:/{print $2}')

# Disk (in GB)
DISK_GB=$(df -BG / | awk 'NR==2 {print $2}' | sed 's/G//')

# Architecture
ARCHITECTURE=$(uname -m)

# OS
if [ -f /etc/os-release ]; then
    OS=$(grep "^PRETTY_NAME=" /etc/os-release | cut -d'"' -f2)
    OS_VERSION=$(grep "^VERSION_ID=" /etc/os-release | cut -d'"' -f2 || echo "unknown")
else
    OS=$(uname -s)
    OS_VERSION=$(uname -r)
fi

# Docker version
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
else
    DOCKER_VERSION=""
fi

# Network interfaces
NETWORK_INTERFACES=$(ip -o link show | awk -F': ' '{print $2}' | grep -v "lo" | tr '\n' ',' | sed 's/,$//')

echo -e "${GREEN}Capabilities detected:${NC}"
echo "  CPU: $CPU_CORES cores ($CPU_MODEL)"
echo "  Memory: ${MEMORY_MB}MB"
echo "  Disk: ${DISK_GB}GB"
echo "  Architecture: $ARCHITECTURE"
echo "  OS: $OS $OS_VERSION"
echo "  Docker: ${DOCKER_VERSION:-Not installed}"
echo "  Network: $NETWORK_INTERFACES"
echo ""

# Build JSON payload
PAYLOAD=$(cat <<EOF
{
  "claim_token": "$CLAIM_TOKEN",
  "device_id": "$DEVICE_ID",
  "name": "$DEVICE_NAME",
  "type": "$DEVICE_TYPE",
  "tailscale_ip": "$TAILSCALE_IP",
  "tailscale_hostname": "$TAILSCALE_HOSTNAME",
  "tailscale_node_id": "$TAILSCALE_NODE_ID",
  "capabilities": {
    "cpu_cores": $CPU_CORES,
    "cpu_model": "$CPU_MODEL",
    "memory_mb": $MEMORY_MB,
    "disk_gb": $DISK_GB,
    "architecture": "$ARCHITECTURE",
    "os": "$OS",
    "os_version": "$OS_VERSION",
    "docker_version": "$DOCKER_VERSION",
    "network_interfaces": ["$(echo $NETWORK_INTERFACES | sed 's/,/","/g')"]
  }
}
EOF
)

# Register device
echo -e "${YELLOW}Registering device with Agentify...${NC}"
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$DEVICE_MANAGER_URL/api/v1/devices/register")

# Check response
if echo "$RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Device registered successfully!${NC}"
    echo ""
    echo -e "${GREEN}Device Details:${NC}"
    echo "$RESPONSE" | jq '.data'
    echo ""
    echo -e "${GREEN}Your device is now ready to receive agent deployments!${NC}"
    exit 0
else
    echo -e "${RED}✗ Registration failed${NC}"
    echo "$RESPONSE" | jq '.'
    exit 1
fi

