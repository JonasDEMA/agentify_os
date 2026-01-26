# Energy Agent

**Agent ID:** `agent.energy.controller`

The Energy Agent is a first-class AI-orchestrable agent that provides comprehensive control and monitoring of energy infrastructure, including EV charging, grid monitoring, and Frequency Containment Reserve (FCR) processes.

## Overview

The Energy Agent wraps the existing Python Energy API with a TypeScript agent layer that follows the Agent Standard v1, enabling natural language control and AI orchestration through the Agent Communication Protocol.

### Key Features

- **EV Charging Control** - Manage charging modes, power limits, and PID tracking
- **Energy Metering** - Monitor real-time energy metrics from loadpoints, meters, and grid
- **Grid Monitoring** - Track grid frequency and voltage for stability
- **FCR Management** - Control Frequency Containment Reserve processes
- **Power Optimization** - Optimize charging based on cost, renewable energy, and grid stability
- **Safety Constraints** - Hard limits prevent dangerous operations
- **Database Integration** - Store all metrics and state in Supabase
- **Infrastructure Integration** - Works with Monitoring, Logging, and Remote Access agents

## Architecture

```
Marketplace Orchestrator (AI)
         ↓
   Energy Agent (TypeScript)
         ↓
   Energy API (Python/FastAPI)
         ↓
   EVCC Service (Go)
         ↓
Physical Infrastructure (EV Chargers, Meters, Grid)
```

## Installation

### Prerequisites

- Node.js 18+
- TypeScript 5+
- Supabase account
- Running Energy API instance
- Running EVCC instance

### Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build:
```bash
npm run build
```

4. Start:
```bash
npm start
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `3000` |
| `ENERGY_API_BASE_URL` | Energy API endpoint | `http://localhost:8000/energy-api/v1` |
| `SUPABASE_URL` | Supabase project URL | Required |
| `SUPABASE_KEY` | Supabase anon key | Required |
| `AGENT_ID` | Agent identifier | `agent.energy.controller` |
| `CUSTOMER_ID` | Customer identifier | `customer-001` |
| `MAX_POWER_LIMIT_W` | Maximum power safety limit | `22080` |
| `MIN_POWER_LIMIT_W` | Minimum power safety limit | `1380` |
| `LOG_LEVEL` | Logging level | `info` |

## Agent Communication Protocol

### Capabilities

1. **ev_charging_control** - Control EV charging modes and power limits
2. **energy_metering** - Monitor real-time energy metrics
3. **grid_monitoring** - Track grid frequency and stability
4. **fcr_management** - Manage FCR processes
5. **power_optimization** - Optimize power usage

### Tools

#### 1. control_ev_charging

Control EV charging for a loadpoint.

**Input:**
```json
{
  "loadpoint_id": 1,
  "mode": "pv",
  "max_power": 11040,
  "enable_tracking": true
}
```

**Output:**
```json
{
  "success": true,
  "loadpoint_id": 1,
  "mode": "pv",
  "max_power": 11040,
  "power_tracking": true
}
```

#### 2. monitor_energy

Get real-time energy metrics.

**Input:**
```json
{
  "source": "loadpoint",
  "source_id": 1
}
```

**Output:**
```json
{
  "source": "loadpoint",
  "metrics": {
    "actual_power": 7360,
    "desired_power": 11040,
    "charging": true,
    "mode": "pv"
  },
  "timestamp": "2026-01-26T10:30:00Z"
}
```

#### 3. manage_fcr

Manage FCR module and process.

**Input:**
```json
{
  "action": "initialize",
  "module_id": "fcr-module-1",
  "power_limit": 80
}
```

**Output:**
```json
{
  "success": true,
  "module_id": "fcr-module-1",
  "status": {
    "ready": true,
    "vehicle_min_power": 1380,
    "vehicle_max_power": 11040
  }
}
```

#### 4. optimize_power

Optimize power usage based on objectives and constraints.

**Input:**
```json
{
  "loadpoint_id": 1,
  "objective": "minimize_cost",
  "constraints": {
    "max_cost_per_kwh": 0.35
  }
}
```

**Output:**
```json
{
  "success": true,
  "loadpoint_id": 1,
  "objective": "minimize_cost",
  "optimized_mode": "pv",
  "optimized_power": 11040,
  "estimated_savings": 0.10,
  "reasoning": "Peak hours (14:00). Using solar-only mode to minimize grid cost."
}
```

**Objectives:**

1. **minimize_cost** - Optimize for lowest energy cost
   - Uses off-peak hours for grid charging
   - Prioritizes solar during peak hours
   - Constraints: `max_cost_per_kwh`

2. **maximize_renewable** - Maximize solar/renewable usage
   - Pure solar mode during daytime
   - Minimal grid usage at night
   - Constraints: `min_renewable_percentage`

3. **balance_grid** - Optimize for grid stability
   - Increases load when frequency is high (excess generation)
   - Reduces load when frequency is low (excess demand)
   - Participates in grid balancing

4. **fast_charge** - Fastest charging within constraints
   - Charges at maximum safe power
   - Respects grid frequency limits
   - Constraints: `target_soc`, `charge_by_time`, `max_power`

## REST API

### Loadpoints

- `GET /api/loadpoints` - List all loadpoints
- `GET /api/loadpoints/:id` - Get loadpoint details
- `POST /api/loadpoints/:id/control` - Control loadpoint

### Health

- `GET /health` - Health check

## Natural Language Examples

### Example 1: Solar-Only Charging
```
User: "Charge my EV using only solar power"
  ↓
Marketplace Orchestrator discovers Energy Agent
  ↓
Energy Agent sets mode to 'pv' for loadpoint
  ↓
User's EV charges using solar only
```

### Example 2: Grid Monitoring
```
User: "What's the current grid frequency?"
  ↓
Energy Agent monitors grid
  ↓
Returns: "Grid frequency is 50.02 Hz - stable"
```

### Example 3: Cost Optimization
```
User: "Charge my EV as cheaply as possible"
  ↓
Marketplace Orchestrator calls optimize_power with objective: minimize_cost
  ↓
Energy Agent analyzes time-of-use pricing
  ↓
Returns: "Off-peak hours. Charging at max power 11040W. Saving 0.20 EUR/h vs peak."
  ↓
User's EV charges during cheapest hours
```

### Example 4: Renewable Optimization
```
User: "Charge my EV with 100% renewable energy"
  ↓
Marketplace Orchestrator calls optimize_power with objective: maximize_renewable
  ↓
Energy Agent checks time of day
  ↓
Returns: "Daytime. Using pure solar mode (pv) for 100% renewable energy."
  ↓
User's EV charges only when solar is available
```

### Example 5: Grid Balancing
```
User: "Help stabilize the grid while charging"
  ↓
Marketplace Orchestrator calls optimize_power with objective: balance_grid
  ↓
Energy Agent checks grid frequency (50.08 Hz - high)
  ↓
Returns: "Grid frequency high. Increasing load to 11040W to absorb excess generation."
  ↓
User's EV helps balance the grid
```

### Example 6: Fast Charge
```
User: "Charge my EV to 80% as fast as possible"
  ↓
Marketplace Orchestrator calls optimize_power with objective: fast_charge, constraints: {target_soc: 80}
  ↓
Energy Agent calculates optimal power
  ↓
Returns: "Fast charge mode. Charging at maximum power 11040W. Estimated time to 80% SOC: 3.2h."
  ↓
User's EV charges at maximum safe power
```

## Database Schema

### energy_metrics

Stores all energy metrics for analysis and monitoring.

### fcr_processes

Tracks FCR module state and initialization.

## Development

### Build
```bash
npm run build
```

### Watch mode
```bash
npm run watch
```

### Development mode
```bash
npm run dev
```

## Infrastructure Integration

The Energy Agent integrates with infrastructure agents for complete observability and management.

### Configuration

Enable infrastructure integration in `.env`:

```bash
ENABLE_INFRASTRUCTURE_INTEGRATION=true
MONITORING_AGENT_URL=http://localhost:3001
LOGGING_AGENT_URL=http://localhost:3002
REMOTE_ACCESS_AGENT_URL=http://localhost:3003
```

### With Monitoring Agent

**Automatic Metrics Collection:**
- EV charging metrics (mode, power, energy, SOC, grid frequency)
- Power optimization metrics (objective, mode, power, savings, renewable %)
- FCR process metrics

**Automatic Alerting:**
- Power limit exceeded (critical)
- Grid frequency out of range (critical)
- Charging mode changed (info)
- Optimization executed (info)

**Setup:**
Alert rules are automatically created on startup when infrastructure integration is enabled.

### With Logging Agent

**Automatic Audit Trail:**
- All charging actions (mode changes, power adjustments)
- All optimization executions (objective, constraints, results)
- All FCR actions (register, initialize, set output)
- Critical errors and warnings

**Log Levels:**
- `info` - Normal operations
- `warning` - Non-critical issues
- `error` - Critical errors requiring attention

**Search:**
Use Logging Agent's search tool to find specific actions:
```json
{
  "tool": "search_logs",
  "parameters": {
    "agent_id": "agent.energy.controller",
    "level": "info",
    "search_term": "optimization"
  }
}
```

### With Remote Access Agent

Remote Access Agent can provide SSH/VNC access to edge devices running Energy Agent for:
- Remote debugging
- Configuration updates
- Log inspection
- Performance monitoring

### Integration Architecture

```
Energy Agent
     │
     ├─► Monitoring Agent (metrics + alerts)
     │   └─► Dashboards, Alerting, Analytics
     │
     ├─► Logging Agent (audit trail)
     │   └─► Log Search, Compliance, Debugging
     │
     └─► Remote Access Agent (remote management)
         └─► SSH/VNC, Configuration, Debugging
```

### Graceful Degradation

If infrastructure agents are unavailable:
- Energy Agent continues normal operation
- Metrics and logs are queued (not sent)
- No errors are thrown
- Warnings are logged locally

This ensures Energy Agent reliability even if infrastructure agents are down.

## License

MIT

