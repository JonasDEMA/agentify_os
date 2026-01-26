#!/bin/bash

###############################################################################
# Agentify Device Heartbeat Script
# 
# This script sends periodic heartbeats to the Device Manager
# Should be run via cron every 1-5 minutes
#
# Usage:
#   ./heartbeat.sh <DEVICE_ID> <DEVICE_MANAGER_URL>
#
# Example cron entry (every 2 minutes):
#   */2 * * * * /path/to/heartbeat.sh raspi-001 https://device-manager.agentify.ai
###############################################################################

set -e

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Error: Missing arguments"
    echo "Usage: $0 <DEVICE_ID> <DEVICE_MANAGER_URL>"
    exit 1
fi

DEVICE_ID=$1
DEVICE_MANAGER_URL=$2

# Collect metrics
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

# Temperature (Raspberry Pi specific)
if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
    TEMPERATURE=$(echo "scale=1; $TEMP/1000" | bc)
else
    TEMPERATURE=0
fi

# Uptime in seconds
UPTIME=$(awk '{print int($1)}' /proc/uptime)

# Load average
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | xargs)
LOAD_1=$(echo $LOAD_AVG | cut -d',' -f1 | xargs)
LOAD_5=$(echo $LOAD_AVG | cut -d',' -f2 | xargs)
LOAD_15=$(echo $LOAD_AVG | cut -d',' -f3 | xargs)

# Check if Tailscale is running
if tailscale status &> /dev/null; then
    STATUS="online"
else
    STATUS="offline"
fi

# Build JSON payload
PAYLOAD=$(cat <<EOF
{
  "status": "$STATUS",
  "metrics": {
    "cpu_usage": $CPU_USAGE,
    "memory_usage": $MEMORY_USAGE,
    "disk_usage": $DISK_USAGE,
    "temperature": $TEMPERATURE,
    "uptime": $UPTIME,
    "load_average": [$LOAD_1, $LOAD_5, $LOAD_15]
  }
}
EOF
)

# Send heartbeat
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$DEVICE_MANAGER_URL/api/v1/devices/$DEVICE_ID/heartbeat" > /dev/null 2>&1

exit 0

