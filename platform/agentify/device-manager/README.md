# 🖥️ Device Manager

**Version:** 1.0.0  
**Status:** ✅ Implemented

---

## 🎯 Overview

The Device Manager is a service that manages edge devices (Raspberry Pi, Linux servers) in the Agentify platform. It handles:
- **Device Registration** - Claim and register new edge devices
- **Tailscale Integration** - Secure mesh VPN connectivity
- **Device Monitoring** - Health checks and heartbeat tracking
- **Device Lifecycle** - Status management and decommissioning

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `TAILSCALE_API_KEY` - Your Tailscale API key
- `TAILSCALE_TAILNET` - Your Tailscale tailnet name

### 3. Run Development Server

```bash
npm run dev
```

### 4. Build for Production

```bash
npm run build
npm start
```

---

## 📡 API Endpoints

### Generate Claim Token

**POST** `/api/v1/devices/claim-token`

Generate a token for claiming a new device.

**Request:**
```json
{
  "customer_id": "customer-123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "claim_token": "abc123...",
    "tailscale_auth_key": "tskey-auth-...",
    "expires_at": "2024-01-22T12:00:00Z",
    "instructions": {
      "step1": "Install Tailscale on your device",
      "step2": "Run: tailscale up --authkey=tskey-auth-...",
      "step3": "Run the Agentify device registration script"
    }
  }
}
```

### Register Device

**POST** `/api/v1/devices/register`

Register a new device using a claim token.

**Request:**
```json
{
  "claim_token": "abc123...",
  "device_id": "raspi-001",
  "name": "Living Room Pi",
  "type": "raspberry_pi",
  "tailscale_ip": "100.64.0.1",
  "tailscale_hostname": "raspi-001",
  "tailscale_node_id": "n123456",
  "capabilities": {
    "cpu_cores": 4,
    "cpu_model": "ARM Cortex-A72",
    "memory_mb": 4096,
    "disk_gb": 32,
    "architecture": "arm64",
    "os": "Raspberry Pi OS",
    "os_version": "11",
    "docker_version": "24.0.0",
    "network_interfaces": ["eth0", "wlan0"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "device_id": "raspi-001",
    "customer_id": "customer-123",
    "name": "Living Room Pi",
    "status": "online",
    "tailscale_ip": "100.64.0.1",
    "created_at": "2024-01-21T12:00:00Z"
  },
  "message": "Device registered successfully"
}
```

### Get Device

**GET** `/api/v1/devices/:device_id`

Get device details.

### List Devices

**GET** `/api/v1/devices`

List all devices with optional filters.

**Query Parameters:**
- `customer_id` - Filter by customer
- `status` - Filter by status (online, offline, claimed, unclaimed)
- `type` - Filter by type (raspberry_pi, generic_linux, other)
- `limit` - Limit results (default: 10)
- `offset` - Offset for pagination

### Update Device

**PUT** `/api/v1/devices/:device_id`

Update device information.

**Request:**
```json
{
  "name": "New Name",
  "metadata": {
    "location": "Living Room"
  }
}
```

### Update Device Status

**PUT** `/api/v1/devices/:device_id/status`

Update device status.

**Request:**
```json
{
  "status": "online"
}
```

### Delete Device

**DELETE** `/api/v1/devices/:device_id`

Delete a device (also removes from Tailscale).

### Device Heartbeat

**POST** `/api/v1/devices/:device_id/heartbeat`

Record device heartbeat with metrics.

**Request:**
```json
{
  "status": "online",
  "metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "disk_usage": 38.5,
    "temperature": 52.3,
    "uptime": 86400,
    "load_average": [0.5, 0.6, 0.7]
  }
}
```

### Get Device Statistics

**GET** `/api/v1/devices/stats`

Get device statistics.

**Query Parameters:**
- `customer_id` - Filter by customer (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 10,
    "online": 8,
    "offline": 2,
    "claimed": 9,
    "unclaimed": 1,
    "by_type": {
      "raspberry_pi": 7,
      "generic_linux": 2,
      "other": 1
    }
  }
}
```

---

## 🔄 Device Claiming Flow

1. **Admin generates claim token** via API
2. **User receives claim token** and Tailscale auth key
3. **User installs Tailscale** on device: `tailscale up --authkey=<key>`
4. **User runs registration script** on device with claim token
5. **Device registers** with Device Manager
6. **Device appears** in customer's device list
7. **Device is ready** for agent deployments

---

## 🗄️ Database Schema

### `devices` Table
```sql
CREATE TABLE devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id TEXT UNIQUE NOT NULL,
  customer_id TEXT NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  status TEXT NOT NULL,
  tailscale_ip TEXT NOT NULL,
  tailscale_hostname TEXT,
  tailscale_node_id TEXT,
  capabilities JSONB NOT NULL,
  metadata JSONB,
  last_seen TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `device_claim_tokens` Table
```sql
CREATE TABLE device_claim_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  token TEXT UNIQUE NOT NULL,
  device_id TEXT,
  customer_id TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  claimed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `device_heartbeats` Table
```sql
CREATE TABLE device_heartbeats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL,
  metrics JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔐 Tailscale Integration

The Device Manager uses Tailscale for secure device connectivity:

- **Mesh VPN** - Direct device-to-device communication
- **No public IPs** - Devices don't need internet-facing IPs
- **Automatic NAT traversal** - Works behind firewalls
- **Encrypted** - All traffic is encrypted
- **Access control** - Tag-based ACLs for security

---

## ✅ Implementation Status

- [x] Project structure
- [x] TypeScript configuration
- [x] Tailscale API client
- [x] Database client
- [x] Device registration API
- [x] Claim token generation
- [x] Device heartbeat system
- [x] Device statistics
- [ ] Device registration script (for edge devices)
- [ ] Web UI for device management
- [ ] Automated health monitoring
- [ ] Alert system for offline devices

---

**Next:** Create device registration script for Raspberry Pi

