# Monitoring Agent

**Agent ID:** `agent.agentify.monitoring`

A first-class infrastructure agent that provides comprehensive monitoring, metrics collection, health checks, and alerting for cloud and edge infrastructure.

## 🎯 Overview

The Monitoring Agent transforms infrastructure monitoring into an AI-orchestrable capability. Instead of manually setting up monitoring tools, the Marketplace Orchestrator can discover and use this agent to collect metrics, check health, and create alerts.

## ✨ Features

### Metrics Collection
- ✅ Collect metrics from Docker containers via Dockerode
- ✅ Collect metrics from edge devices via HTTP/Tailscale
- ✅ CPU, memory, disk, network metrics
- ✅ Automatic snapshot storage
- ✅ Configurable collection intervals

### Health Monitoring
- ✅ Health checks for containers and devices
- ✅ CPU, memory, disk threshold checks
- ✅ Temperature monitoring (Raspberry Pi)
- ✅ Overall health score (0-100)
- ✅ Health status: Healthy, Degraded, Unhealthy

### Alerting
- ✅ Alert rule engine with threshold conditions
- ✅ Alert severity levels: Info, Warning, Critical, Emergency
- ✅ Multiple notification channels (webhook, email, agent message)
- ✅ Alert acknowledgment and resolution
- ✅ Auto-resolve when condition clears
- ✅ Duration-based alerts (condition must persist)

### Dashboard Data
- ✅ Time series data aggregation
- ✅ Summary statistics (avg, min, max)
- ✅ Configurable time ranges
- ✅ Multiple metric support

## 🚀 Quick Start

### Installation

```bash
cd platform/agentify/monitoring
npm install
```

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `PORT` - Server port (default: 3005)

### Development

```bash
npm run dev
```

### Production

```bash
npm run build
npm start
```

## 📡 API Endpoints

### Agent Communication Protocol

**POST** `/agent/message`

Handle agent messages with intents:
- `collect_metrics` - Collect metrics from source
- `check_health` - Check health status
- `create_alert` - Create alert rule
- `get_dashboard_data` - Get dashboard data
- `get_stats` - Get statistics

### REST API

#### Metrics
- **POST** `/api/v1/metrics/collect` - Collect metrics
- **GET** `/api/v1/metrics/:source_id` - Get metrics

#### Health
- **POST** `/api/v1/health/check` - Check health
- **GET** `/api/v1/health/:source_id` - Get health status

#### Alert Rules
- **POST** `/api/v1/alerts/rules` - Create alert rule
- **GET** `/api/v1/alerts/rules` - List alert rules
- **PUT** `/api/v1/alerts/rules/:rule_id` - Update alert rule
- **DELETE** `/api/v1/alerts/rules/:rule_id` - Delete alert rule

#### Alerts
- **GET** `/api/v1/alerts` - List alerts
- **POST** `/api/v1/alerts/:alert_id/acknowledge` - Acknowledge alert
- **POST** `/api/v1/alerts/:alert_id/resolve` - Resolve alert

#### Dashboard
- **POST** `/api/v1/dashboard` - Get dashboard data
- **GET** `/api/v1/stats/:customer_id` - Get statistics

#### Health Check
- **GET** `/health` - Service health check

## 📊 Usage Examples

### Collect Metrics via Agent Protocol

```json
POST /agent/message
{
  "id": "msg-123",
  "type": "request",
  "sender": "agent.marketplace.orchestrator",
  "to": ["agent.agentify.monitoring"],
  "intent": "collect_metrics",
  "payload": {
    "source_type": "container",
    "source_id": "container-abc123",
    "customer_id": "customer-123"
  }
}
```

### Create Alert Rule

```json
POST /api/v1/alerts/rules
{
  "customer_id": "customer-123",
  "name": "High CPU Alert",
  "description": "Alert when CPU usage exceeds 80%",
  "condition": {
    "metric_name": "cpu_usage_percent",
    "operator": "gt",
    "threshold": 80,
    "duration_seconds": 300
  },
  "severity": "warning",
  "channels": ["https://webhook.example.com/alerts", "ops@example.com"]
}
```

### Check Health

```json
POST /api/v1/health/check
{
  "source_type": "device",
  "source_id": "device-xyz789",
  "customer_id": "customer-123"
}
```

### Get Dashboard Data

```json
POST /api/v1/dashboard
{
  "customer_id": "customer-123",
  "source_id": "container-abc123",
  "time_range": {
    "start": "2026-01-22T00:00:00Z",
    "end": "2026-01-22T23:59:59Z"
  },
  "metrics": ["cpu_usage_percent", "memory_usage_percent"],
  "aggregation": "avg"
}
```

## 🗄️ Database Schema

### Tables

1. **`metrics`** - Individual metric data points
   - id, timestamp, source_type, source_id, customer_id
   - metric_name, metric_type, value, unit
   - labels, metadata

2. **`metrics_snapshots`** - Complete system snapshots
   - id, timestamp, source_type, source_id, customer_id
   - cpu_usage_percent, memory_usage_percent, disk_usage_percent
   - network_rx_bytes, network_tx_bytes, uptime_seconds
   - load_average, temperature

3. **`health_checks`** - Health check results
   - id, timestamp, source_type, source_id, customer_id
   - status, checks, overall_score

4. **`alert_rules`** - Alert rule definitions
   - id, customer_id, name, description
   - source_type, source_id, condition, severity
   - channels, enabled, created_at, updated_at

5. **`alerts`** - Triggered alerts
   - id, rule_id, customer_id, source_type, source_id
   - severity, status, title, message
   - metric_value, threshold, triggered_at
   - acknowledged_at, acknowledged_by, resolved_at

## 🔄 Background Jobs

- **Metrics Collection** - Every 1 minute
- **Health Checks** - Every 5 minutes
- **Alert Evaluation** - Every 30 seconds
- **Metrics Cleanup** - Daily at 2 AM

## 🏗️ Architecture

```
Monitoring Agent
├── Metrics Collector (Dockerode + HTTP)
├── Health Checker (Threshold-based)
├── Alert Engine (Rule evaluation + Notifications)
├── Database Client (Supabase)
└── Express Server (Agent Protocol + REST API)
```

## 🔐 Security

- Customer isolation (all queries filtered by customer_id)
- No metric tampering (hard constraint)
- Accurate metrics collection (hard constraint)
- Timely alert delivery (hard constraint)

## 📝 License

MIT

