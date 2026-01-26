# 🚀 Agentify Edge Integration - Implementation Roadmap

**Project:** Integrate e-conomy.io edge infrastructure with Agentify platform
**Goal:** Enable AI-orchestrated deployment of agent teams to Railway (cloud) and edge devices (Raspberry Pi)
**Status:** 🚧 In Progress
**Version:** 1.0.0
**Date:** 2026-01-21

---

## 📋 **Project Overview**

Transform infrastructure components into intelligent agents that can be discovered, composed, and deployed by AI through natural language requests.

### **Key Innovation**
Instead of manually configuring infrastructure, users describe what they need:
> "I need the following stack: on an edge device a new application called 14a (German law) that sends a signal to an EMS which then realizes it."

The system automatically:
1. Discovers application agents (14a, EMS)
2. Auto-suggests infrastructure agents (remote access, logging, monitoring)
3. Deploys to appropriate target (Railway or edge device)
4. Connects everything via agent communication protocol

---

## 🎯 **Architecture Components**

### **1. Hosting Agent (NEW)**
- Orchestrates deployments to Railway (cloud) and edge devices
- Manages container lifecycles
- Tracks deployment status

### **2. Device Management (EXTENDED)**
- Registers edge devices (Raspberry Pi)
- Tracks device capabilities and status
- Routes deployments to appropriate devices
- Uses Tailscale for secure connectivity (no public IPs needed)

### **3. Infrastructure Agents (NEW CATEGORY)**
- Remote Access Agent (pi-tunnel/Tailscale wrapper)
- Logging Agent (log collection/forwarding)
- Monitoring Agent (metrics/alerts)
- Energy API Agent (energy management)
- EVCC Agent (EV charging control)
- Database Agents (MongoDB, InfluxDB)

### **4. Marketplace Orchestrator (ENHANCED)**
- Natural language requirement parsing
- Device-aware agent discovery
- Auto-suggestion of baseline infrastructure agents
- Team composition with dependencies

### **5. Agent Router (NEW)**
- Routes messages between cloud and edge agents
- Handles cloud ↔ edge communication
- Connection management via Tailscale

---

## 📊 **Implementation Phases**

## ✅ **Phase 1: Core Infrastructure** (Weeks 1-2)

### 1.1 Hosting Agent - Railway Deployment
- [x] Create Hosting Agent base structure
  - [x] Set up project structure in `platform/agentify/hosting/`
  - [x] Create `manifest.json` for Hosting Agent
  - [x] Implement base orchestrator with Agent Standard v1
- [x] Implement Railway deployer
  - [x] Railway API client integration
  - [x] Container deployment logic
  - [x] Environment variable management
  - [x] Health check implementation
- [x] Deployment status tracking
  - [x] Database schema for deployments
  - [x] Status update webhooks
  - [x] Deployment logs collection
- [ ] Testing
  - [ ] Unit tests for Railway deployer
  - [ ] Integration tests with sample agents
  - [ ] End-to-end deployment test

### 1.2 Hosting Agent - Edge Deployment
- [x] Create Edge deployer
  - [x] Docker container deployment logic
  - [x] Container orchestration (without K3s/ArgoCD)
  - [x] Volume management for persistent data
  - [x] Network configuration
- [x] Implement deployment templates
  - [x] Application agent template
  - [x] Infrastructure agent template
  - [x] Multi-container stack template
- [x] Resource management
  - [x] CPU/memory limits
  - [x] Disk space monitoring
  - [x] Container restart policies
- [ ] Testing
  - [ ] Local Docker deployment tests
  - [ ] Resource limit validation
  - [ ] Multi-container deployment test

### 1.3 Device Management System
- [x] Create Device Registry
  - [x] Database schema for edge devices
    - [x] Device ID, name, type (raspberry_pi, etc.)
    - [x] Capabilities (hardware specs, installed software)
    - [x] Status (online, offline, deploying)
    - [x] Tailscale connection info
    - [x] Customer/organization association
  - [x] Device registration API endpoints
    - [x] POST `/api/v1/devices/register`
    - [x] GET `/api/v1/devices/{device_id}`
    - [x] GET `/api/v1/devices` (list with filters)
    - [x] PUT `/api/v1/devices/{device_id}/status`
  - [x] Device capability discovery
    - [x] Hardware detection (CPU, RAM, disk)
    - [x] Software detection (Docker, installed agents)
    - [x] Network capability detection
- [x] Implement Tailscale integration
  - [x] Tailscale API client
  - [x] Device authentication via Tailscale
  - [x] Automatic Tailscale setup on device registration
  - [x] Connection status monitoring
  - [x] IP address management via Tailscale
- [x] Device claiming flow
  - [x] Generate device claim tokens
  - [x] Web-based device claiming UI
  - [x] Device ownership transfer
  - [x] Multi-tenant device isolation
- [x] Device health monitoring
  - [x] Heartbeat mechanism
  - [x] Connection status tracking
  - [x] Resource usage monitoring
  - [x] Alert system for offline devices
- [ ] Testing
  - [ ] Device registration flow test
  - [ ] Tailscale connection test
  - [ ] Multi-device management test
  - [ ] Device claiming flow test

### 1.4 Agent Router
- [x] Create Agent Router service
  - [x] Message routing logic
  - [x] Agent location registry (cloud vs edge)
  - [x] Connection pool management
- [x] Implement cloud-to-edge routing
  - [x] Tailscale-based communication
  - [x] Message queuing for offline devices
  - [x] Retry logic with exponential backoff
- [x] Implement edge-to-cloud routing
  - [x] Outbound message handling
  - [x] Response correlation
  - [x] Timeout management
- [x] Agent discovery across boundaries
  - [x] Cross-location agent lookup
  - [x] Capability-based routing
  - [x] Load balancing for multi-instance agents
- [ ] Testing
  - [ ] Cloud-to-edge message routing test
  - [ ] Edge-to-cloud message routing test
  - [ ] Offline device message queuing test
  - [ ] Multi-hop routing test

---

## ⚡ **Phase 2: Infrastructure Agents** (Weeks 2-3)

### 2.1 Remote Access Agent
- [x] Create Remote Access Agent
  - [x] Agent manifest with capabilities: `remote_ssh`, `remote_vnc`, `tunnel_management`
  - [x] Wrapper for Tailscale SSH
  - [x] Session management (create, list, terminate)
  - [x] Access control and authentication
- [x] Implement agent tools
  - [x] `create_ssh_session` - Create SSH tunnel to device
  - [x] `create_vnc_session` - Create VNC tunnel for GUI access
  - [x] `list_sessions` - List active remote sessions
  - [x] `terminate_session` - Close remote session
- [x] Security features
  - [x] Session timeout management
  - [x] Audit logging for all access
  - [x] Role-based access control
  - [ ] Multi-factor authentication support
- [ ] Testing
  - [ ] SSH tunnel creation test
  - [ ] Session timeout test
  - [ ] Access control validation
  - [ ] Concurrent session handling test

### 2.2 Logging Agent
- [x] Create Logging Agent
  - [x] Agent manifest with capabilities: `log_collection`, `log_forwarding`, `log_search`
  - [x] Log collection from containers
  - [x] Log aggregation and forwarding
  - [x] Log retention policies
- [x] Implement agent tools
  - [x] `collect_logs` - Collect logs from specified agent/container
  - [x] `search_logs` - Search logs with filters (time, level, keyword)
  - [x] `stream_logs` - Real-time log streaming
  - [x] `export_logs` - Export logs to external systems
- [x] Integration with logging backends
  - [x] Supabase logging integration
  - [x] Local file-based logging for edge devices
  - [ ] Log rotation and compression
- [ ] Testing
  - [ ] Log collection from multiple containers
  - [ ] Log search with complex filters
  - [ ] Real-time log streaming test
  - [ ] Log retention policy enforcement

### 2.3 Monitoring Agent ✅
- [x] Create Monitoring Agent
  - [x] Agent manifest with capabilities: `metrics_collection`, `alerting`, `health_checks`
  - [x] Metrics collection (CPU, RAM, disk, network)
  - [x] Alert rule engine
  - [x] Dashboard data provider
- [x] Implement agent tools
  - [x] `collect_metrics` - Collect system/container metrics
  - [x] `create_alert_rule` - Define alert conditions
  - [x] `check_health` - Perform health checks on agents
  - [x] `get_dashboard_data` - Provide metrics for dashboards
- [x] Alert system
  - [x] Alert rule definitions (threshold, anomaly detection)
  - [x] Alert notification channels (email, webhook, agent message)
  - [x] Alert history and acknowledgment
- [ ] Testing
  - [ ] Metrics collection accuracy test
  - [ ] Alert triggering test
  - [ ] Health check reliability test
  - [ ] Dashboard data aggregation test

---

## 🔋 **Phase 3: Energy Agents** (Weeks 3-4)

### 3.1 Energy Agent Core ✅ **COMPLETE**
**Status:** ✅ COMPLETE
**Completed:** 2026-01-26
**Location:** `platform/agentify/agents/energy/`

**Implementation:**
- [x] Create Energy Agent
  - [x] Agent manifest with capabilities: `ev_charging_control`, `energy_metering`, `grid_monitoring`, `fcr_management`, `power_optimization`
  - [x] TypeScript wrapper for existing Python Energy API
  - [x] Agent Communication Protocol support
  - [x] Supabase database integration
- [x] Implement agent tools
  - [x] `control_ev_charging` - Control EV charging mode and power limits
  - [x] `monitor_energy` - Get real-time metrics from loadpoints/meters/grid
  - [x] `manage_fcr` - Manage FCR processes (register, initialize, control)
  - [ ] `optimize_power` - Optimize power usage (TODO - Phase 3.2)
- [x] Core modules
  - [x] `energy-api-client.ts` - HTTP client wrapping Python Energy API (206 lines)
  - [x] `ev-controller.ts` - EV charging control with safety checks (200 lines)
  - [x] `fcr-manager.ts` - FCR process management (170 lines)
  - [x] `database.ts` - Supabase integration for metrics and state (150 lines)
  - [x] `types.ts` - Complete TypeScript type definitions (150 lines)
  - [x] `index.ts` - Express server with Agent Communication Protocol (150 lines)
- [x] Safety features
  - [x] Power limit validation (MAX_POWER_LIMIT_W, MIN_POWER_LIMIT_W)
  - [x] Charging mode validation
  - [x] Grid frequency constraints
  - [x] Error handling and logging
- [x] Documentation
  - [x] README.md with examples and API documentation
  - [x] IMPLEMENTATION_STATUS.md with detailed status tracking

**Natural Language Examples:**
```
"Charge my EV using only solar power"
→ Energy Agent sets mode to 'pv' for loadpoint

"What's the current grid frequency?"
→ Energy Agent monitors grid and returns frequency

"Initialize FCR module with 80% power limit"
→ Energy Agent registers and initializes FCR process
```

### 3.2 Power Optimization ✅ **COMPLETE**
**Status:** ✅ COMPLETE
**Completed:** 2026-01-26
**Location:** `platform/agentify/agents/energy/src/optimizer.ts`

**Goal:** Implement the `optimize_power` tool with intelligent optimization algorithms.

**Implementation:**
- [x] Create optimizer module
  - [x] `optimizer.ts` - Power optimization engine (348 lines)
  - [x] Cost calculation with time-of-use pricing
  - [x] Renewable energy optimization
  - [x] Grid stability scoring with frequency monitoring
- [x] Implement optimization objectives
  - [x] `minimize_cost` - Time-of-use pricing, peak/off-peak awareness
  - [x] `maximize_renewable` - Daytime solar prioritization, nighttime grid minimization
  - [x] `balance_grid` - Grid frequency-based load adjustment
  - [x] `fast_charge` - Maximum safe power with grid frequency checks
- [x] Constraint handling
  - [x] Max cost constraints (max_cost_per_kwh)
  - [x] Min renewable percentage (min_renewable_percentage)
  - [x] Grid frequency limits (safety checks)
  - [x] Vehicle battery limits (target_soc)
  - [x] Time constraints (charge_by_time)
  - [x] Power limits (max_power)
- [x] Integration
  - [x] Connected to Energy API for real-time data
  - [x] Placeholder for pricing APIs (extensible)
  - [x] Placeholder for solar forecast APIs (extensible)
  - [x] Updated `index.ts` to route optimize_power tool
- [x] Features
  - [x] Automatic mode selection (off, now, pv, minpv)
  - [x] Automatic power limit adjustment
  - [x] Power tracking enablement
  - [x] Detailed reasoning for decisions
  - [x] Metrics storage in database

**Natural Language Examples:**
```
"Charge my EV as cheaply as possible"
→ Optimizer analyzes time-of-use pricing
→ Off-peak: charges at max power
→ Peak: uses solar-only mode

"Charge with 100% renewable energy"
→ Optimizer checks time of day
→ Daytime: pure solar mode (pv)
→ Nighttime: charging disabled or minimal grid

"Help stabilize the grid while charging"
→ Optimizer monitors grid frequency
→ High frequency: increases load
→ Low frequency: reduces load

"Charge to 80% as fast as possible"
→ Optimizer calculates max safe power
→ Estimates charge time
→ Charges at maximum power
```

### 3.3 Infrastructure Integration ✅ **COMPLETE**
**Status:** ✅ COMPLETE
**Completed:** 2026-01-26
**Priority:** High

**Goal:** Integrate Energy Agent with existing infrastructure agents for complete observability.

**Implementation:**
- [x] Create integration module
  - [x] `infrastructure-integration.ts` - Integration module (313 lines)
  - [x] Agent Communication Protocol client for all infrastructure agents
  - [x] Graceful degradation when agents unavailable
- [x] Monitoring Agent integration
  - [x] Configure metrics collection for all operations
  - [x] Set up alerts for power limits (critical)
  - [x] Set up alerts for grid frequency (critical)
  - [x] Set up alerts for mode changes (info)
  - [x] Set up alerts for optimizations (info)
  - [x] Automatic alert creation on startup
- [x] Logging Agent integration
  - [x] Configure log forwarding via Agent Communication Protocol
  - [x] Audit trail for charging actions
  - [x] Audit trail for optimization executions
  - [x] Audit trail for FCR actions
  - [x] Critical error logging
- [x] Remote Access Agent integration
  - [x] Client initialized for remote debugging
  - [x] Configuration for remote access URL
- [x] Integration with Energy Agent tools
  - [x] `control_ev_charging` - sends metrics and logs
  - [x] `monitor_energy` - sends energy metrics
  - [x] `manage_fcr` - sends FCR logs
  - [x] `optimize_power` - sends optimization metrics and logs
- [x] Configuration
  - [x] Updated `.env.example` with integration settings
  - [x] `ENABLE_INFRASTRUCTURE_INTEGRATION` flag
- [x] Documentation
  - [x] Updated README.md with integration details
  - [x] Updated IMPLEMENTATION_STATUS.md

**Features:**
- **Automatic Metrics** - All operations send metrics to Monitoring Agent
- **Automatic Alerts** - Alert rules created on startup
- **Automatic Audit Trail** - All actions logged to Logging Agent
- **Graceful Degradation** - Works even if infrastructure agents unavailable

**Natural Language Examples:**
```
"Show me charging metrics for the last hour"
→ Monitoring Agent returns metrics from Energy Agent

"Why did charging mode change?"
→ Logging Agent searches audit trail
→ Shows: "Optimization: maximize_renewable"

"Alert me if grid frequency is critical"
→ Already configured on startup
→ Alerts when frequency < 49.8 Hz or > 50.2 Hz
```

### 3.4 EVCC Agent ✅ **COMPLETE**
- [x] Create EVCC Agent
  - [x] Agent manifest with capabilities: `loadpoint_control`, `site_management`, `vehicle_management`, `charging_optimization`, `energy_monitoring`
  - [x] Hybrid wrapper for EVCC (Electric Vehicle Charge Controller) via REST API
  - [x] TypeScript client for EVCC REST API (315 lines)
  - [x] Loadpoint controller with safety validation (207 lines)
  - [x] Site manager for grid/PV/battery management (171 lines)
  - [x] Vehicle manager for charging plans (165 lines)
  - [x] Charging optimizer with 4 algorithms (283 lines)
- [x] Implement agent tools
  - [x] `control_loadpoint` - Control charging mode, current, SOC, phases with safety checks
  - [x] `get_system_status` - Get complete system status (site + loadpoints)
  - [x] `set_charging_plan` - Schedule charging with target SOC/energy and deadline
  - [x] `manage_battery` - Configure battery buffer SOC and discharge control
  - [x] `optimize_charging` - Intelligent optimization with 4 objectives
- [x] Smart charging features
  - [x] **minimize_cost** - Off-peak charging, PV priority, peak avoidance
  - [x] **maximize_pv** - Scale charging power based on PV production (5kW+ = 3p/32A, 2-5kW = 3p/16A, 1-2kW = 1p/10A, <1kW = minpv)
  - [x] **balance_grid** - Reduce grid stress, consume excess power locally
  - [x] **fast_charge** - Maximum safe power (3-phase 32A or 1-phase 32A)
- [x] Infrastructure Integration
  - [x] Monitoring Agent integration (metrics collection, alerts)
  - [x] Logging Agent integration (audit trail)
  - [x] Remote Access Agent integration (remote debugging)
  - [x] Default alerts (high grid power, charging failure, low battery SOC)
- [x] Database Integration
  - [x] Supabase integration with 4 tables
  - [x] Loadpoint state tracking
  - [x] Charging session history
  - [x] Optimization decision history
  - [x] System state snapshots
- [x] Safety Features
  - [x] Current limits validation (6A-32A)
  - [x] SOC limits validation (0-100%)
  - [x] Phase switching blocked while charging (prevents charger damage)
  - [x] Graceful degradation when infrastructure agents unavailable
- [x] Documentation
  - [x] README.md with setup guide and natural language examples
  - [x] IMPLEMENTATION_STATUS.md with feature list and testing checklist
- [ ] Testing (Next Step)
  - [ ] Manual testing with real EVCC instance
  - [ ] Unit tests for all modules
  - [ ] Integration tests
  - [ ] Performance testing

**Natural Language Examples:**
```
"Charge my car using only solar power"
→ control_loadpoint with mode="pv"

"Charge as cheaply as possible by tomorrow morning"
→ optimize_charging with objective="minimize_cost" + set_charging_plan

"Stop exporting power to the grid, use it to charge my car instead"
→ optimize_charging with objective="balance_grid"

"Charge to 80% by 7am tomorrow"
→ set_charging_plan with target_soc=80, target_time="2024-01-15T07:00:00Z"
```


### 3.5 Database Agents (Future Phase)
- [ ] Create MongoDB Agent
  - [ ] Agent manifest with capabilities: `document_storage`, `query_execution`, `backup_management`
  - [ ] Wrapper for MongoDB operations
  - [ ] Query interface via agent protocol
- [ ] Create InfluxDB Agent
  - [ ] Agent manifest with capabilities: `timeseries_storage`, `metrics_query`, `data_retention`
  - [ ] Wrapper for InfluxDB operations
  - [ ] Time-series data management
- [ ] Implement common database tools
  - [ ] `store_data` - Store data in database
  - [ ] `query_data` - Query data with filters
  - [ ] `backup_database` - Create database backup
  - [ ] `restore_database` - Restore from backup
- [ ] Testing
  - [ ] Data storage and retrieval test
  - [ ] Query performance test
  - [ ] Backup and restore test
  - [ ] Multi-tenant data isolation test

---


## 🛒 **Phase 4: Marketplace Integration** (Weeks 4-5)

### 4.1 Marketplace Orchestrator Enhancements
- [ ] Natural language requirement parsing
  - [ ] Extend marketplace AI to parse deployment requirements
  - [ ] Extract application needs (14a, EMS, etc.)
  - [ ] Extract deployment target (cloud vs edge)
  - [ ] Extract constraints (location, resources, etc.)
- [ ] Device-aware agent discovery
  - [ ] Extend `discover_agents()` with deployment target filter
  - [ ] Add device capability matching
  - [ ] Filter agents by deployment compatibility
- [ ] Auto-suggestion logic
  - [ ] Define baseline infrastructure agent sets
    - [ ] Edge baseline: [Remote Access, Logging, Monitoring]
    - [ ] Energy baseline: [Energy API, Database]
    - [ ] EV baseline: [EVCC, Energy API, Database]
  - [ ] Implement auto-suggestion algorithm
  - [ ] User confirmation flow for suggestions
- [ ] Team composition with dependencies
  - [ ] Dependency graph resolution
  - [ ] Deployment order determination
  - [ ] Circular dependency detection
- [ ] Testing
  - [ ] Natural language parsing accuracy test
  - [ ] Auto-suggestion relevance test
  - [ ] Dependency resolution test
  - [ ] End-to-end team composition test

### 4.2 Agent Listing Updates
- [ ] Extend Agent model
  - [ ] Add `deployment_targets` field: ["railway", "edge", "both"]
  - [ ] Add `auto_install` field: boolean (for infrastructure agents)
  - [ ] Add `dependencies` field: list of required agent IDs
  - [ ] Add `hardware_requirements` field: {cpu, ram, disk, arch}
- [ ] Update agent manifests
  - [ ] Update all infrastructure agent manifests
  - [ ] Update energy agent manifests
  - [ ] Add deployment metadata to existing agents
- [ ] Create infrastructure agents category
  - [ ] Add "infrastructure" category to marketplace
  - [ ] Tag all infrastructure agents
  - [ ] Create category-specific search filters
- [ ] Testing
  - [ ] Agent model validation test
  - [ ] Manifest schema validation test
  - [ ] Category filtering test
  - [ ] Deployment target filtering test

### 4.3 Deployment Templates
- [ ] Create deployment templates
  - [ ] Edge energy management template
    - [ ] 14a Agent + EMS Agent + Energy API + Monitoring + Logging
  - [ ] EV charging template
    - [ ] EVCC Agent + Energy API + MongoDB + Monitoring
  - [ ] Basic edge application template
    - [ ] Custom Agent + Remote Access + Logging + Monitoring
- [ ] Template management API
  - [ ] POST `/api/v1/templates` - Create template
  - [ ] GET `/api/v1/templates` - List templates
  - [ ] GET `/api/v1/templates/{id}` - Get template details
  - [ ] POST `/api/v1/templates/{id}/deploy` - Deploy from template
- [ ] Template customization
  - [ ] Parameter substitution
  - [ ] Optional component selection
  - [ ] Resource allocation customization
- [ ] Testing
  - [ ] Template deployment test
  - [ ] Parameter substitution test
  - [ ] Template validation test
  - [ ] Multi-template deployment test

---

## 🧪 **Phase 5: Testing & Documentation** (Week 5-6)

### 5.1 End-to-End Testing
- [ ] Create test scenarios
  - [ ] Scenario 1: Deploy 14a + EMS to edge device
  - [ ] Scenario 2: Deploy EV charging stack to edge device
  - [ ] Scenario 3: Deploy mixed cloud + edge agent team
  - [ ] Scenario 4: Device offline/online handling
- [ ] Integration testing
  - [ ] Cloud-to-edge communication test
  - [ ] Agent discovery across boundaries test
  - [ ] Multi-device deployment test
  - [ ] Failover and recovery test
- [ ] Performance testing
  - [ ] Message routing latency test
  - [ ] Concurrent deployment test
  - [ ] Resource usage under load test
  - [ ] Network bandwidth optimization test
- [ ] Security testing
  - [ ] Authentication and authorization test
  - [ ] Multi-tenant isolation test
  - [ ] Tailscale security validation
  - [ ] Audit logging verification

### 5.2 Documentation
- [ ] User documentation
  - [ ] Device registration guide
  - [ ] Agent deployment guide
  - [ ] Marketplace usage guide
  - [ ] Troubleshooting guide
- [ ] Developer documentation
  - [ ] Infrastructure agent development guide
  - [ ] Agent wrapper template
  - [ ] Deployment template creation guide
  - [ ] API reference documentation
- [ ] Architecture documentation
  - [ ] System architecture diagrams
  - [ ] Communication flow diagrams
  - [ ] Database schema documentation
  - [ ] Security architecture documentation
- [ ] Operations documentation
  - [ ] Deployment procedures
  - [ ] Monitoring and alerting setup
  - [ ] Backup and recovery procedures
  - [ ] Scaling guidelines

### 5.3 Demo & Training
- [ ] Create demo environment
  - [ ] Set up demo edge device (Raspberry Pi)
  - [ ] Deploy sample agent stack
  - [ ] Create demo user accounts
  - [ ] Prepare demo scripts
- [ ] Training materials
  - [ ] Video tutorials
  - [ ] Interactive walkthroughs
  - [ ] Sample code and templates
  - [ ] FAQ documentation

---

## 💰 **Billing Strategy for Edge-Deployed Agents**

### Option 1: Usage-Based Billing
**Model:** Pay per agent-hour on edge devices

**Pricing Structure:**
- Infrastructure agents: $0.05/hour per agent
- Application agents: $0.10-0.50/hour per agent (based on complexity)
- Database agents: $0.15/hour per agent + storage fees

**Pros:**
- Fair pricing based on actual usage
- Encourages efficient resource usage
- Easy to understand and predict costs

**Cons:**
- Requires accurate usage tracking
- May be complex for users with many agents
- Billing calculations can be complex

**Implementation:**
- [ ] Usage tracking in Hosting Agent
- [ ] Hourly billing calculation
- [ ] Usage dashboard for customers
- [ ] Automated billing integration

---
### Option 2: Subscription Tiers
**Model:** Monthly subscription based on device count and agent limits

**Tiers:**
- **Starter**: $29/month
  - 1 edge device
  - Up to 5 agents
  - Basic infrastructure agents included
  - Community support

- **Professional**: $99/month
  - Up to 5 edge devices
  - Up to 25 agents
  - All infrastructure agents included
  - Email support
  - Advanced monitoring

- **Enterprise**: $499/month
  - Unlimited edge devices
  - Unlimited agents
  - All agents included
  - Priority support
  - Custom integrations
  - SLA guarantees

**Pros:**
- Predictable monthly costs
- Simple to understand
- Encourages platform adoption

**Cons:**
- May not fit all use cases
- Users may pay for unused capacity
- Hard to scale pricing for large deployments

**Implementation:**
- [ ] Subscription management system
- [ ] Device/agent limit enforcement
- [ ] Tier upgrade/downgrade flow
- [ ] Feature gating by tier

---

### Option 3: Hybrid Model (RECOMMENDED)
**Model:** Base subscription + usage-based add-ons

**Base Subscription:**
- **Edge Starter**: $19/month
  - 1 edge device included
  - 3 infrastructure agents included (Remote Access, Logging, Monitoring)
  - 5 GB data transfer/month

- **Edge Pro**: $79/month
  - 3 edge devices included
  - All infrastructure agents included
  - 50 GB data transfer/month
  - Advanced features (auto-scaling, templates)

**Usage-Based Add-Ons:**
- Additional edge devices: $10/device/month
- Application agents: $0.10/hour per agent
- Energy agents: $0.20/hour per agent
- Data transfer overage: $0.10/GB
- Database storage: $0.25/GB/month

**Pros:**
- Predictable base cost with flexibility
- Fair pricing for variable usage
- Encourages infrastructure agent adoption
- Scales well for different customer sizes

**Cons:**
- More complex billing logic
- Requires both subscription and usage tracking

**Implementation:**
- [ ] Subscription + usage tracking system
- [ ] Overage calculation and alerts
- [ ] Unified billing dashboard
- [ ] Automated invoicing

---

### Option 4: Resource-Based Pricing
**Model:** Pay for actual resource consumption

**Pricing:**
- CPU: $0.05/vCPU-hour
- Memory: $0.01/GB-hour
- Storage: $0.25/GB/month
- Network: $0.10/GB transferred

**Pros:**
- Most fair and transparent
- Aligns with actual costs
- Encourages optimization

**Cons:**
- Complex to understand
- Unpredictable costs
- Requires detailed resource tracking

**Implementation:**
- [ ] Resource metering system
- [ ] Real-time cost estimation
- [ ] Budget alerts and limits
- [ ] Resource optimization recommendations

---

### Recommended Billing Strategy

**Use Hybrid Model (Option 3) with the following features:**

1. **Base Subscription** - Covers infrastructure and platform access
2. **Usage-Based Application Agents** - Pay for what you use
3. **Included Infrastructure Agents** - Encourage best practices
4. **Data Transfer Limits** - Prevent abuse, charge for overages
5. **Volume Discounts** - Reward large deployments
6. **Marketplace Revenue Sharing** - 70/30 split for third-party agents

**Additional Features:**
- [ ] Real-time cost dashboard
- [ ] Budget alerts and limits
- [ ] Cost optimization recommendations
- [ ] Detailed usage reports
- [ ] Annual billing discount (15% off)
- [ ] Free tier for development/testing

---

## 📋 **Appendix A: Technical Specifications**

### Agent Communication Protocol
- **Transport**: HTTP/HTTPS, WebSocket
- **Format**: JSON (AgentMessage)
- **Authentication**: CoreSense IAM + JWT tokens
- **Message Types**: REQUEST, INFORM, DISCOVER, OFFER, ACCEPT, REJECT, COMPLETE

### Deployment Targets
- **Railway**: Cloud container platform
- **Edge Device**: Raspberry Pi 4/5 (4GB+ RAM recommended)
- **Container Runtime**: Docker 24+
- **Network**: Tailscale mesh VPN

### Database Schema Extensions

**devices table:**
```sql
CREATE TABLE devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL, -- 'raspberry_pi', 'jetson_nano', etc.
  customer_id TEXT NOT NULL,
  tailscale_ip TEXT,
  tailscale_hostname TEXT,
  status TEXT NOT NULL, -- 'online', 'offline', 'deploying'
  capabilities JSONB, -- {cpu, ram, disk, arch, installed_software}
  last_heartbeat TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**deployments table:**
```sql
CREATE TABLE deployments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deployment_id TEXT UNIQUE NOT NULL,
  agent_id TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  target_type TEXT NOT NULL, -- 'railway', 'edge'
  target_id TEXT, -- device_id for edge, railway_service_id for cloud
  status TEXT NOT NULL, -- 'pending', 'deploying', 'running', 'failed'
  config JSONB, -- deployment configuration
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 📋 **Appendix B: Agent Manifest Examples**

### Remote Access Agent Manifest
```json
{
  "agent_id": "agent.infrastructure.remote-access",
  "name": "Remote Access Agent",
  "version": "1.0.0",
  "category": "infrastructure",
  "deployment_targets": ["edge"],
  "auto_install": true,
  "capabilities": ["remote_ssh", "remote_vnc", "tunnel_management"],
  "dependencies": [],
  "hardware_requirements": {
    "cpu": "0.1",
    "memory": "128Mi",
    "disk": "100Mi",
    "arch": ["arm64", "amd64"]
  },
  "tools": [
    {
      "name": "create_ssh_session",
      "description": "Create SSH tunnel to device",
      "parameters": {
        "device_id": "string",
        "port": "number"
      }
    }
  ]
}
```

### 14a Agent Manifest
```json
{
  "agent_id": "agent.energy.14a",
  "name": "14a Grid Regulation Agent",
  "version": "1.0.0",
  "category": "energy",
  "deployment_targets": ["edge"],
  "auto_install": false,
  "capabilities": ["grid_signal_reception", "load_reduction", "compliance_reporting"],
  "dependencies": ["agent.energy.energy-api", "agent.infrastructure.monitoring"],
  "hardware_requirements": {
    "cpu": "0.5",
    "memory": "512Mi",
    "disk": "1Gi",
    "arch": ["arm64", "amd64"]
  },
  "tools": [
    {
      "name": "receive_grid_signal",
      "description": "Receive signal from grid operator",
      "parameters": {
        "signal_type": "string",
        "reduction_level": "number"
      }
    }
  ]
}
```

---

## 📋 **Appendix C: Deployment Flow Diagrams**

### Cloud Deployment Flow
```
User Request → Marketplace Orchestrator
  ↓
Parse Requirements & Discover Agents
  ↓
Auto-Suggest Infrastructure Agents
  ↓
User Confirms Agent Team
  ↓
Marketplace → Hosting Agent (REQUEST: deploy_to_railway)
  ↓
Hosting Agent → Railway API
  ↓
Railway Creates Container
  ↓
Hosting Agent ← Railway (webhook: deployment_complete)
  ↓
Hosting Agent → Marketplace (INFORM: deployment_complete)
  ↓
Marketplace → User (notification)
```

### Edge Deployment Flow
```
User Request → Marketplace Orchestrator
  ↓
Parse Requirements & Discover Agents
  ↓
Auto-Suggest Infrastructure Agents
  ↓
User Confirms Agent Team + Selects Device
  ↓
Marketplace → Hosting Agent (REQUEST: deploy_to_edge)
  ↓
Hosting Agent → Agent Router (route to device)
  ↓
Agent Router → Edge Device (via Tailscale)
  ↓
Edge Device: Docker Pull & Run
  ↓
Edge Device → Agent Router (INFORM: container_started)
  ↓
Agent Router → Hosting Agent
  ↓
Hosting Agent → Marketplace (INFORM: deployment_complete)
  ↓
Marketplace → User (notification)
```

---

## 🎯 **Next Steps**

1. **Review this roadmap** with the team
2. **Prioritize phases** based on business needs
3. **Set up project tracking** (GitHub Projects, Jira, etc.)
4. **Begin Phase 1** implementation
5. **Schedule weekly progress reviews**

---

**Status:** 📋 Ready for Review
**Version:** 1.0.0
**Date:** 2026-01-21
**Author:** Agentify Team


