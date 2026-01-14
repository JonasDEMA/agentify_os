# 🚀 CPA Agent Platform - Deployment Guide

**Version:** 1.0.0  
**Date:** 2026-01-14  
**Status:** Production Ready

---

## 📋 **Table of Contents**

1. [Overview](#overview)
2. [Cloud Deployment](#cloud-deployment)
3. [Edge Deployment](#edge-deployment)
4. [Desktop Deployment](#desktop-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring & Observability](#monitoring--observability)

---

## 🎯 **Overview**

The **CPA Agent Platform** supports **universal deployment** - the same agent runs identically on Cloud, Edge, and Desktop with **zero code changes**.

### **Deployment Targets**

| Target | Use Case | Examples |
|--------|----------|----------|
| **Cloud** | Scalable, always-on agents | Railway, AWS, Azure, GCP |
| **Edge** | Low-latency, local processing | IoT devices, Raspberry Pi, Edge servers |
| **Desktop** | User-specific automation | Windows, macOS, Linux workstations |

### **Key Principles**

1. **Same Manifest**: One `manifest.json` for all environments
2. **Same Code**: No environment-specific code changes
3. **Same Ethics**: Identical compliance enforcement everywhere
4. **Same Behavior**: Guaranteed consistent execution

---

## ☁️ **Cloud Deployment**

Deploy agents to cloud platforms for scalable, always-on operation.

### **Railway Deployment**

**1. Create `railway.toml`**

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "agent-std run manifest.json"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[env]
AGENT_MANIFEST = "manifest.json"
ETHICS_STRICT_MODE = "true"
LOG_LEVEL = "INFO"
```

**2. Deploy**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

**3. Monitor**

```bash
# View logs
railway logs

# Check status
railway status
```

---

### **AWS Lambda Deployment**

**1. Create `lambda_handler.py`**

```python
from core.agent_standard import Agent
import json

# Load agent
agent = Agent.from_manifest("manifest.json")

def lambda_handler(event, context):
    """AWS Lambda handler."""
    result = agent.execute(event)
    
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
```

**2. Package**

```bash
# Install dependencies
pip install -r requirements.txt -t package/

# Copy code
cp -r core/ package/
cp manifest.json package/
cp lambda_handler.py package/

# Create ZIP
cd package && zip -r ../lambda.zip . && cd ..
```

**3. Deploy**

```bash
# Create function
aws lambda create-function \
  --function-name my-agent \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role

# Update
aws lambda update-function-code \
  --function-name my-agent \
  --zip-file fileb://lambda.zip
```

---

### **Docker Deployment**

**1. Create `Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY core/ ./core/
COPY manifest.json .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "from core.agent_standard import Agent; Agent.from_manifest('manifest.json')"

# Run agent
CMD ["agent-std", "run", "manifest.json"]
```

**2. Build & Run**

```bash
# Build
docker build -t my-agent:latest .

# Run
docker run -d \
  --name my-agent \
  -e ETHICS_STRICT_MODE=true \
  -v ./logs:/app/logs \
  my-agent:latest

# Logs
docker logs -f my-agent
```

**3. Deploy to Registry**

```bash
# Tag
docker tag my-agent:latest registry.example.com/my-agent:latest

# Push
docker push registry.example.com/my-agent:latest
```

---

## 🌐 **Edge Deployment**

Deploy agents to edge devices for low-latency, local processing.

### **Raspberry Pi Deployment**

**1. Install Dependencies**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv -y

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install agent platform
pip install -r requirements.txt
```

**2. Configure Systemd Service**

```bash
# Create service file
sudo nano /etc/systemd/system/my-agent.service
```

```ini
[Unit]
Description=CPA Agent Platform
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/my-agent
Environment="PATH=/home/pi/my-agent/venv/bin"
ExecStart=/home/pi/my-agent/venv/bin/agent-std run manifest.json
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. Start Service**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable my-agent

# Start service
sudo systemctl start my-agent

# Check status
sudo systemctl status my-agent

# View logs
sudo journalctl -u my-agent -f
```

---

### **IoT Device Deployment (Docker)**

```bash
# Pull image (ARM architecture)
docker pull --platform linux/arm64 my-agent:latest

# Run
docker run -d \
  --name my-agent \
  --restart unless-stopped \
  -e AGENT_MANIFEST=/app/manifest.json \
  -v ./manifest.json:/app/manifest.json \
  -v ./logs:/app/logs \
  my-agent:latest
```

---

## 🖥️ **Desktop Deployment**

Deploy agents to user workstations for desktop automation.

### **Windows Deployment**

**1. Install Python**

```powershell
# Download Python 3.11 from python.org
# Or use winget
winget install Python.Python.3.11
```

**2. Install Agent Platform**

```powershell
# Clone repository
git clone https://github.com/JonasDEMA/cpa_agent_platform.git
cd cpa_agent_platform

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**3. Run Agent**

```powershell
# Run directly
agent-std run manifest.json

# Or as background service (NSSM)
nssm install MyAgent "C:\path\to\venv\Scripts\agent-std.exe" "run manifest.json"
nssm start MyAgent
```

---

### **macOS Deployment**

**1. Install Python**

```bash
# Using Homebrew
brew install python@3.11
```

**2. Install Agent Platform**

```bash
# Clone repository
git clone https://github.com/JonasDEMA/cpa_agent_platform.git
cd cpa_agent_platform

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**3. Run as LaunchAgent**

```bash
# Create plist file
nano ~/Library/LaunchAgents/com.mycompany.agent.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mycompany.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/agent-std</string>
        <string>run</string>
        <string>manifest.json</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/agent</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

```bash
# Load service
launchctl load ~/Library/LaunchAgents/com.mycompany.agent.plist

# Start service
launchctl start com.mycompany.agent
```

---

## ⚙️ **Environment Configuration**

Configure agents for different environments using environment variables.

### **Environment Variables**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AGENT_MANIFEST` | Path to manifest.json | `manifest.json` | Yes |
| `ETHICS_STRICT_MODE` | Enforce strict ethics | `false` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `OVERSIGHT_ENDPOINT` | Oversight API endpoint | - | No |
| `HEALTH_CHECK_INTERVAL` | Health check interval (sec) | `300` | No |
| `ESCALATION_WEBHOOK` | Webhook for escalations | - | No |

### **Configuration Files**

**`.env` (Development)**

```bash
AGENT_MANIFEST=manifest.json
ETHICS_STRICT_MODE=false
LOG_LEVEL=DEBUG
HEALTH_CHECK_INTERVAL=60
```

**`.env.production` (Production)**

```bash
AGENT_MANIFEST=manifest.json
ETHICS_STRICT_MODE=true
LOG_LEVEL=INFO
HEALTH_CHECK_INTERVAL=300
OVERSIGHT_ENDPOINT=https://oversight.example.com/api
ESCALATION_WEBHOOK=https://alerts.example.com/webhook
```

---

## 📊 **Monitoring & Observability**

Monitor agent health, ethics compliance, and performance.

### **Health Checks**

**CLI Health Check**

```bash
# Check agent health
agent-std health

# Output:
# Status: healthy
# Tension: 0.35
# Desires:
#   - trust: 0.75
#   - helpfulness: 0.65
#   - coherence: 0.70
```

### **Logging**

**Structured Logging**

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 🔒 **Security Best Practices**

### **1. Secrets Management**

```bash
# Use environment variables for secrets
export SMTP_PASSWORD="secret"
export API_KEY="secret"
```

### **2. Ethics Enforcement**

```bash
# Always enable strict mode in production
export ETHICS_STRICT_MODE=true
```

---

## 📚 **Resources**

- **GitHub**: https://github.com/JonasDEMA/cpa_agent_platform
- **Agent Standard Spec**: [core/agent_standard/README.md](core/agent_standard/README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Happy Deploying! 🚀**

