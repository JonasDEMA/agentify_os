# EVCC Agent

**Agent ID:** `agent.evcc.controller`  
**Version:** 1.0.0  
**Category:** Infrastructure Agent

## Overview

The EVCC Agent is a TypeScript wrapper around the [EVCC](https://evcc.io) (EV Charge Controller) Go application, transforming it into a first-class AI-orchestrable agent following the Agent Standard v1. It provides intelligent EV charging control, optimization, and energy management capabilities through natural language.

## Architecture

**Hybrid Wrapper Pattern:**
- **EVCC Go Service** - Mature, production-ready EV charging controller (runs separately)
- **EVCC Agent** - TypeScript agent wrapper that communicates via EVCC's REST API
- **Agent Communication Protocol** - Standardized messaging for AI orchestration

## Capabilities

### 1. **Loadpoint Control** (`loadpoint_control`)
Control individual EV charging points with safety validation.

**Features:**
- Set charging mode (off, now, minpv, pv)
- Configure current limits (6A-32A)
- Set SOC and energy limits
- Switch between 1-phase and 3-phase charging
- Safety constraints (no phase switching while charging)

### 2. **Site Management** (`site_management`)
Manage overall energy system (grid, PV, battery).

**Features:**
- Monitor grid, PV, battery, and home power
- Configure battery buffer SOC
- Control battery discharge
- Set grid charge limits

### 3. **Vehicle Management** (`vehicle_management`)
Manage EV charging plans and schedules.

**Features:**
- Set target SOC or energy
- Schedule charging with deadlines
- Estimate charging duration
- Vehicle-specific settings

### 4. **Charging Optimization** (`charging_optimization`)
Intelligent charging optimization with multiple objectives.

**Objectives:**
- **minimize_cost** - Charge during off-peak hours or when PV available
- **maximize_pv** - Maximize solar energy usage
- **balance_grid** - Help balance grid load and reduce stress
- **fast_charge** - Charge as quickly as possible (safely)

### 5. **Energy Monitoring** (`energy_monitoring`)
Real-time monitoring of energy flows and charging status.

**Metrics:**
- Grid power (import/export)
- PV production
- Battery state and power
- Home consumption
- Charging power and energy

## Tools

### `control_loadpoint`
Control a specific charging point.

**Parameters:**
- `loadpoint_id` (number, required) - Loadpoint identifier
- `mode` (string, optional) - Charging mode: off, now, minpv, pv
- `min_current` (number, optional) - Minimum current in Amperes (6-32A)
- `max_current` (number, optional) - Maximum current in Amperes (6-32A)
- `limit_soc` (number, optional) - SOC limit percentage (0-100)
- `limit_energy` (number, optional) - Energy limit in kWh
- `phases` (number, optional) - Number of phases: 1 or 3

**Example:**
```json
{
  "loadpoint_id": 1,
  "mode": "pv",
  "max_current": 16,
  "limit_soc": 80,
  "phases": 3
}
```

### `get_system_status`
Get complete system status including all loadpoints and site energy.

**Returns:**
- Site status (grid, PV, battery, home power)
- All loadpoints with charging status
- Vehicle information

### `set_charging_plan`
Set a charging plan with target and deadline.

**Parameters:**
- `loadpoint_id` (number, required)
- `target_time` (string, required) - ISO 8601 datetime
- `target_soc` (number, optional) - Target SOC percentage
- `target_energy` (number, optional) - Target energy in kWh

**Example:**
```json
{
  "loadpoint_id": 1,
  "target_time": "2024-01-15T07:00:00Z",
  "target_soc": 80
}
```

### `manage_battery`
Manage home battery settings.

**Parameters:**
- `buffer_soc` (number, optional) - Buffer SOC percentage
- `buffer_start_soc` (number, optional) - Buffer start SOC percentage
- `discharge_control` (boolean, optional) - Enable/disable discharge control
- `grid_charge_limit` (number, optional) - Grid charge limit in Watts

### `optimize_charging`
Optimize charging based on objective.

**Parameters:**
- `loadpoint_id` (number, required)
- `objective` (string, required) - minimize_cost, maximize_pv, balance_grid, fast_charge
- `constraints` (object, optional) - max_power, target_soc, deadline

**Example:**
```json
{
  "loadpoint_id": 1,
  "objective": "maximize_pv",
  "constraints": {
    "target_soc": 80
  }
}
```

## Natural Language Examples

**"Charge my car using only solar power"**
→ `control_loadpoint` with mode="pv"

**"Charge as cheaply as possible by tomorrow morning"**
→ `optimize_charging` with objective="minimize_cost" + `set_charging_plan` with deadline

**"What's my current charging status?"**
→ `get_system_status`

**"Stop exporting power to the grid, use it to charge my car instead"**
→ `optimize_charging` with objective="balance_grid"

**"Charge to 80% by 7am tomorrow"**
→ `set_charging_plan` with target_soc=80, target_time="2024-01-15T07:00:00Z"

## Setup

### Prerequisites

1. **EVCC** - Running EVCC instance (v0.120.0+)
2. **Node.js** - v18 or higher
3. **Supabase** - PostgreSQL database for state tracking
4. **Infrastructure Agents** (optional) - Monitoring, Logging, Remote Access

### Installation

```bash
cd platform/agentify/agents/evcc
npm install
```

### Configuration

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Server
PORT=3004

# EVCC
EVCC_URL=http://localhost:7070

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Safety Limits
MAX_CURRENT_LIMIT_A=32
MIN_CURRENT_LIMIT_A=6

# Infrastructure Integration (optional)
ENABLE_INFRASTRUCTURE_INTEGRATION=true
MONITORING_AGENT_URL=http://localhost:3001
LOGGING_AGENT_URL=http://localhost:3002
REMOTE_ACCESS_AGENT_URL=http://localhost:3003
```

### Database Setup

The agent will create these tables in Supabase:

- `evcc_loadpoints` - Loadpoint state tracking
- `evcc_charging_sessions` - Charging session history
- `evcc_optimization_history` - Optimization decision history
- `evcc_system_state` - System state snapshots

### Running

```bash
# Development
npm run dev

# Production
npm run build
npm start
```

## Integration

### With EVCC

The agent communicates with EVCC via its REST API:

```
EVCC Agent → HTTP → EVCC Go Service → Charger/Meter/Vehicle
```

### With Infrastructure Agents

When enabled, the agent automatically:
- Sends metrics to Monitoring Agent
- Sends logs to Logging Agent
- Creates alert rules for critical conditions
- Enables remote debugging via Remote Access Agent

### With Marketplace Orchestrator

The agent registers with the Marketplace Orchestrator for AI-powered discovery and team composition.

## Safety Features

### Hard Constraints (Ethics)

1. **Current Limits** - Never exceed 6A-32A range
2. **Phase Switching** - Never switch phases while actively charging
3. **Battery Protection** - Never discharge home battery below buffer SOC
4. **Validation** - All parameters validated before execution

### Graceful Degradation

- Works without infrastructure agents
- Handles EVCC connection failures
- Validates all inputs before execution

## Development

### Project Structure

```
platform/agentify/agents/evcc/
├── manifest.json              # Agent Standard v1 manifest
├── package.json
├── tsconfig.json
├── .env.example
├── src/
│   ├── index.ts              # Main Express server
│   ├── evcc-client.ts        # EVCC REST API client
│   ├── loadpoint-controller.ts
│   ├── site-manager.ts
│   ├── vehicle-manager.ts
│   ├── charging-optimizer.ts
│   ├── infrastructure-integration.ts
│   ├── database.ts
│   └── logger.ts
└── README.md
```

### Testing

```bash
# Run tests (when implemented)
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

## License

MIT

