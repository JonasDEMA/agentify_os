# 🔐 Remote Access Agent

**Version:** 1.0.0  
**Status:** ✅ Implemented

---

## 🎯 Overview

The Remote Access Agent is an infrastructure agent that provides secure SSH and VNC access to edge devices through Tailscale. It transforms remote access into a first-class agent capability that can be discovered and orchestrated by AI.

**Key Features:**
- **SSH Access** - Create secure SSH tunnels to edge devices
- **VNC Access** - Create VNC tunnels for GUI access
- **Session Management** - Track and manage active remote sessions
- **Access Control** - Role-based access control with policies
- **Audit Logging** - Comprehensive audit trail for all access
- **Session Timeout** - Automatic session expiration
- **Agent Communication Protocol** - Full integration with Agentify platform

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

### Agent Communication Protocol

**POST** `/agent/message`

Handle agent messages with the following intents:
- `create_ssh_session` - Create SSH session
- `create_vnc_session` - Create VNC session
- `list_sessions` - List sessions
- `get_session` - Get session details
- `terminate_session` - Terminate session

**Example Request:**
```json
{
  "id": "msg-123",
  "ts": "2026-01-21T12:00:00Z",
  "type": "request",
  "sender": "agent.marketplace.orchestrator",
  "to": ["agent.agentify.remote-access"],
  "intent": "create_ssh_session",
  "payload": {
    "device_id": "raspi-001",
    "user_id": "user-123",
    "customer_id": "customer-123",
    "duration_minutes": 60,
    "purpose": "Debug application issue"
  }
}
```

**Example Response:**
```json
{
  "id": "msg-124",
  "ts": "2026-01-21T12:00:01Z",
  "type": "inform",
  "sender": "agent.agentify.remote-access",
  "to": ["agent.marketplace.orchestrator"],
  "intent": "create_ssh_session",
  "payload": {
    "session_id": "session-abc123",
    "type": "ssh",
    "connection_info": {
      "host": "100.64.0.1",
      "port": 22,
      "ssh_command": "ssh root@100.64.0.1"
    },
    "expires_at": "2026-01-21T13:00:00Z"
  }
}
```

### REST API Endpoints

#### Create SSH Session
**POST** `/api/v1/sessions/ssh`

```json
{
  "device_id": "raspi-001",
  "user_id": "user-123",
  "customer_id": "customer-123",
  "duration_minutes": 60,
  "purpose": "Debug application"
}
```

#### Create VNC Session
**POST** `/api/v1/sessions/vnc`

```json
{
  "device_id": "raspi-001",
  "user_id": "user-123",
  "customer_id": "customer-123",
  "duration_minutes": 60,
  "purpose": "GUI access for configuration"
}
```

#### List Sessions
**GET** `/api/v1/sessions?user_id=user-123&status=active`

#### Get Session
**GET** `/api/v1/sessions/:session_id`

#### Terminate Session
**DELETE** `/api/v1/sessions/:session_id`

```json
{
  "user_id": "user-123"
}
```

#### Get Audit Logs
**GET** `/api/v1/audit-logs?user_id=user-123&limit=100`

#### Get Statistics
**GET** `/api/v1/stats`

---

## 🔒 Security Features

### Access Control
- **Policy-Based Access** - Users must have access policy to create sessions
- **Device Restrictions** - Policies can restrict access to specific devices
- **Session Type Control** - Control which session types (SSH/VNC) are allowed

### Audit Logging
All actions are logged:
- Session creation (success/failure)
- Session termination
- Access denied events
- Policy updates

### Session Management
- **Automatic Expiration** - Sessions expire after configured duration
- **Maximum Duration** - Configurable max session duration (default: 8 hours)
- **Background Cleanup** - Expired sessions are automatically cleaned up

### Authentication
- **Required Authentication** - All requests require authentication
- **MFA Support** - Multi-factor authentication recommended
- **Role-Based Access** - Users must have `remote-access-user` role

---

## 🗄️ Database Schema

### `remote_access_sessions` Table
```sql
CREATE TABLE remote_access_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type TEXT NOT NULL,
  device_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  purpose TEXT NOT NULL,
  status TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  terminated_at TIMESTAMPTZ,
  connection_info JSONB NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `access_policies` Table
```sql
CREATE TABLE access_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  device_ids TEXT[] NOT NULL,
  allowed_session_types TEXT[] NOT NULL,
  max_duration_minutes INTEGER NOT NULL,
  requires_approval BOOLEAN DEFAULT FALSE,
  requires_mfa BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `remote_access_audit_logs` Table
```sql
CREATE TABLE remote_access_audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID,
  user_id TEXT NOT NULL,
  device_id TEXT,
  action TEXT NOT NULL,
  status TEXT NOT NULL,
  details JSONB NOT NULL,
  ip_address TEXT,
  user_agent TEXT,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🎯 Agent Capabilities

The Remote Access Agent exposes the following capabilities:

- `remote_ssh` - Create and manage SSH tunnels
- `remote_vnc` - Create and manage VNC tunnels
- `tunnel_management` - Manage active sessions
- `access_control` - Role-based access control
- `audit_logging` - Comprehensive audit logging

---

## 🔄 Usage Flow

### 1. User Requests Access
```
User → Marketplace Orchestrator → Remote Access Agent
```

### 2. Access Validation
```
Remote Access Agent checks:
- User has access policy
- Device is in allowed list
- Device is online
- SSH/VNC is enabled on device
```

### 3. Session Creation
```
Remote Access Agent:
- Creates session record
- Generates connection info
- Sets expiration time
- Logs audit entry
```

### 4. User Connects
```
User uses connection info:
- SSH: ssh root@100.64.0.1
- VNC: vnc://100.64.0.1:5900
```

### 5. Session Expiration
```
Background job:
- Checks for expired sessions every 60s
- Updates status to 'expired'
- Logs audit entry
```

---

## ✅ Implementation Status

- [x] Project structure
- [x] Agent manifest with capabilities
- [x] TypeScript configuration
- [x] Type definitions
- [x] Database client
- [x] Session manager (SSH + VNC)
- [x] Access control
- [x] Audit logging
- [x] Session expiration
- [x] Agent Communication Protocol
- [x] REST API endpoints
- [x] Background jobs
- [ ] MFA integration
- [ ] Approval workflow
- [ ] WebSocket for real-time updates

---

**Next:** Deploy to production and integrate with Marketplace Orchestrator

