# 🎨 Lovable UI Integration Guide - CPA Server

## 📋 Übersicht

Diese Anleitung beschreibt **Schritt für Schritt**, wie du die CPA Server API in Lovable integrierst.

**Ziel:** Eine moderne Web-UI zum Monitoring und Management von CPA Agents.

---

## 🔑 Admin Token

**Agent ID:** `admin_lovable_ui`

**API Key:** `cpa_admin_lovable_ui_2025_secure_token_zav2DtpZy2zTlaY-DSetzHr5jiHOfOKKo5_n-E_UkbA`

⚠️ **Wichtig:** Dieser Token ist in `.admin_token.txt` gespeichert (nicht committen!)

---

## 🚀 Railway Deployment

### ✅ Checklist: Server auf Railway deployen

- [ ] **1. Railway Account erstellen**
  - Gehe zu https://railway.app
  - Sign up mit GitHub

- [ ] **2. Neues Projekt erstellen**
  - "New Project" → "Deploy from GitHub repo"
  - Repository auswählen: `Agentify/01_CPA`

- [ ] **3. Environment Variables setzen**
  ```env
  HOST=0.0.0.0
  PORT=$PORT
  DEBUG=false
  DATABASE_URL=sqlite+aiosqlite:///./cpa_server.db
  SECRET_KEY=<generiere-random-string>
  CORS_ORIGINS=["https://your-lovable-app.lovable.app"]
  ```

- [ ] **4. Build Command konfigurieren**
  - Settings → Build Command:
  ```bash
  pip install poetry && poetry install --no-dev
  ```

- [ ] **5. Start Command konfigurieren**
  - Settings → Start Command:
  ```bash
  poetry run python -m server.main
  ```

- [ ] **6. Datenbank seeden**
  - Nach erstem Deploy:
  ```bash
  railway run poetry run python server/db/seed.py
  ```
  - Admin Token kopieren!

- [ ] **7. Domain notieren**
  - Railway generiert URL: `https://your-app.railway.app`
  - Diese URL brauchst du für Lovable

- [ ] **8. API testen**
  - Öffne: `https://your-app.railway.app/docs`
  - Teste: `GET /health` → sollte `{"status": "healthy"}` zurückgeben

---

## 🎨 Lovable UI Setup

### ✅ Checklist: Lovable Projekt erstellen

- [ ] **1. Lovable Account erstellen**
  - Gehe zu https://lovable.dev
  - Sign up

- [ ] **2. Neues Projekt erstellen**
  - "New Project"
  - Name: "CPA Monitor"
  - Template: "React + TypeScript + Vite"

- [ ] **3. Environment Variables setzen**
  - Settings → Environment Variables:
  ```env
  VITE_CPA_API_URL=https://your-app.railway.app
  VITE_CPA_API_KEY=cpa_admin_lovable_ui_2025_secure_token_zav2DtpZy2zTlaY-DSetzHr5jiHOfOKKo5_n-E_UkbA
  ```

- [ ] **4. Dependencies installieren**
  - In Lovable Chat:
  ```
  Install these packages:
  - @tanstack/react-query
  - axios
  - date-fns
  - lucide-react
  - recharts (for charts)
  ```

---

## 🔌 API Integration

### ✅ Checklist: API Client erstellen

- [ ] **1. API Client Datei erstellen**
  - Datei: `src/lib/api.ts`
  - Siehe Code unten

- [ ] **2. React Query Setup**
  - Datei: `src/lib/queryClient.ts`
  - Siehe Code unten

- [ ] **3. API Hooks erstellen**
  - Datei: `src/hooks/useAgents.ts`
  - Datei: `src/hooks/useLogs.ts`
  - Datei: `src/hooks/useScreenshots.ts`
  - Siehe Code unten

---

## 📝 Code Templates

### 1. API Client (`src/lib/api.ts`)

```typescript
import axios from 'axios';

const API_URL = import.meta.env.VITE_CPA_API_URL;
const API_KEY = import.meta.env.VITE_CPA_API_KEY;

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`,
  },
});

// Types
export interface Agent {
  id: string;
  hostname: string;
  os_name: string;
  os_version: string;
  ip_address: string;
  registered_at: string;
  last_seen_at: string;
  is_active: boolean;
  current_task: string | null;
  cpu_count: number;
  memory_total_gb: number;
  screen_resolution: string;
  has_vision: boolean;
  has_ocr: boolean;
  has_ui_automation: boolean;
  phone_number: string | null;
}

export interface LogEntry {
  id: number;
  agent_id: string;
  timestamp: string;
  level: string;
  message: string;
  task_goal: string | null;
  metadata: Record<string, any> | null;
}

export interface Screenshot {
  id: number;
  agent_id: string;
  timestamp: string;
  action_type: string;
  mouse_x: number;
  mouse_y: number;
  task_goal: string | null;
  filename: string;
  file_size_bytes: number;
  url: string;
}

// API Functions
export const agentsApi = {
  getAll: () => api.get<Agent[]>('/api/v1/agents/'),
  getById: (id: string) => api.get<Agent>(`/api/v1/agents/${id}`),
};

export const logsApi = {
  getAll: (params?: { agent_id?: string; level?: string; skip?: number; limit?: number }) =>
    api.get<LogEntry[]>('/api/v1/logs/', { params }),
  stream: (agentId: string, sinceId: number = 0) =>
    api.get<LogEntry[]>(`/api/v1/logs/${agentId}/stream`, { params: { since_id: sinceId } }),
};

export const screenshotsApi = {
  getAll: (params?: { agent_id?: string; action_type?: string; skip?: number; limit?: number }) =>
    api.get<Screenshot[]>('/api/v1/screenshots/', { params }),
  getLatest: (agentId: string, limit: number = 10) =>
    api.get<Screenshot[]>(`/api/v1/screenshots/${agentId}/latest`, { params: { limit } }),
};
```

### 2. React Query Setup (`src/lib/queryClient.ts`)

```typescript
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5000,
    },
  },
});
```

### 3. Agents Hook (`src/hooks/useAgents.ts`)

```typescript
import { useQuery } from '@tanstack/react-query';
import { agentsApi } from '@/lib/api';

export const useAgents = () => {
  return useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await agentsApi.getAll();
      return response.data;
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });
};

export const useAgent = (id: string) => {
  return useQuery({
    queryKey: ['agent', id],
    queryFn: async () => {
      const response = await agentsApi.getById(id);
      return response.data;
    },
    refetchInterval: 5000,
  });
};
```

### 4. Logs Hook (`src/hooks/useLogs.ts`)

```typescript
import { useQuery } from '@tanstack/react-query';
import { logsApi } from '@/lib/api';
import { useState, useEffect } from 'react';

export const useLogs = (agentId?: string, level?: string) => {
  return useQuery({
    queryKey: ['logs', agentId, level],
    queryFn: async () => {
      const response = await logsApi.getAll({ agent_id: agentId, level, limit: 100 });
      return response.data;
    },
    refetchInterval: 2000, // Refresh every 2 seconds
  });
};

// Streaming logs (polling)
export const useLogStream = (agentId: string) => {
  const [logs, setLogs] = useState<any[]>([]);
  const [lastId, setLastId] = useState(0);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await logsApi.stream(agentId, lastId);
        const newLogs = response.data;
        
        if (newLogs.length > 0) {
          setLogs(prev => [...prev, ...newLogs]);
          setLastId(newLogs[newLogs.length - 1].id);
        }
      } catch (error) {
        console.error('Failed to fetch logs:', error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [agentId, lastId]);

  return logs;
};
```

### 5. Screenshots Hook (`src/hooks/useScreenshots.ts`)

```typescript
import { useQuery } from '@tanstack/react-query';
import { screenshotsApi } from '@/lib/api';

export const useScreenshots = (agentId?: string, actionType?: string) => {
  return useQuery({
    queryKey: ['screenshots', agentId, actionType],
    queryFn: async () => {
      const response = await screenshotsApi.getAll({ agent_id: agentId, action_type: actionType, limit: 50 });
      return response.data;
    },
    refetchInterval: 5000,
  });
};

export const useLatestScreenshots = (agentId: string, limit: number = 10) => {
  return useQuery({
    queryKey: ['screenshots', 'latest', agentId, limit],
    queryFn: async () => {
      const response = await screenshotsApi.getLatest(agentId, limit);
      return response.data;
    },
    refetchInterval: 3000,
  });
};
```

---

## 🎨 UI Components

### ✅ Checklist: UI Komponenten erstellen

- [ ] **1. Dashboard Page**
  - Zeigt alle Agents als Karten
  - Status: Online/Offline (last_seen_at < 5 min = online)
  - Current Task
  - Click → Agent Detail Page

- [ ] **2. Agent Detail Page**
  - Agent Info (OS, IP, Hardware)
  - Live Log Stream (Auto-Scroll)
  - Screenshot Gallery (Before/After)
  - Task History

- [ ] **3. Log Viewer Component**
  - Farbcodierung nach Level:
    - 🔵 info → blue
    - 🟢 success → green
    - 🟡 warning → yellow
    - 🔴 error → red
    - 🟣 thinking → purple
  - Filter nach Level
  - Auto-Scroll zu neuesten Logs

- [ ] **4. Screenshot Viewer Component**
  - Grid Layout
  - Before/After Vergleich (Side-by-Side)
  - Mauszeiger-Position anzeigen
  - Zoom-Funktion
  - Lightbox für Vollbild

- [ ] **5. Agent Status Badge**
  - Grün = Online (last_seen_at < 5 min)
  - Grau = Offline
  - Pulsing Animation für Online

---

## 🎯 Lovable Prompts

### Prompt 1: Setup

```
Create a CPA Agent Monitoring Dashboard with:

1. Install dependencies:
   - @tanstack/react-query
   - axios
   - date-fns
   - lucide-react

2. Create API client in src/lib/api.ts with:
   - Base URL from VITE_CPA_API_URL
   - API Key from VITE_CPA_API_KEY in Authorization header
   - Types for Agent, LogEntry, Screenshot
   - API functions for agents, logs, screenshots

3. Setup React Query in src/lib/queryClient.ts

4. Create hooks:
   - useAgents() - fetch all agents, refetch every 5s
   - useLogs(agentId, level) - fetch logs, refetch every 2s
   - useScreenshots(agentId) - fetch screenshots, refetch every 5s
```

### Prompt 2: Dashboard

```
Create Dashboard page with:

1. Grid of Agent Cards showing:
   - Hostname
   - OS (icon + name)
   - Status badge (green=online if last_seen_at < 5min, gray=offline)
   - Current task
   - IP address
   - Click → navigate to /agent/:id

2. Use useAgents() hook
3. Auto-refresh every 5 seconds
4. Loading skeleton while fetching
5. Empty state if no agents
```

### Prompt 3: Agent Detail

```
Create Agent Detail page (/agent/:id) with:

1. Header with:
   - Agent hostname
   - Status badge
   - OS info
   - Hardware info (CPU, RAM, Screen)

2. Tabs:
   - "Live Logs" - Log stream with auto-scroll
   - "Screenshots" - Gallery with before/after comparison
   - "System Info" - Full agent details

3. Live Logs Tab:
   - Use useLogStream(agentId) hook
   - Color-coded by level (info=blue, success=green, warning=yellow, error=red, thinking=purple)
   - Auto-scroll to bottom
   - Filter by level

4. Screenshots Tab:
   - Grid layout
   - Show before/after side-by-side
   - Click to open lightbox
   - Show mouse position overlay
```

---

## ✅ Testing Checklist

- [ ] **1. API Connection**
  - [ ] Dashboard lädt Agents
  - [ ] Agent Detail lädt Details
  - [ ] Logs werden gestreamt
  - [ ] Screenshots werden angezeigt

- [ ] **2. Real-time Updates**
  - [ ] Agents aktualisieren sich alle 5s
  - [ ] Logs aktualisieren sich alle 2s
  - [ ] Screenshots aktualisieren sich alle 5s

- [ ] **3. UI/UX**
  - [ ] Status Badge zeigt korrekt Online/Offline
  - [ ] Log Colors sind korrekt
  - [ ] Screenshots sind sichtbar
  - [ ] Auto-Scroll funktioniert

- [ ] **4. Error Handling**
  - [ ] API Fehler werden angezeigt
  - [ ] Loading States sind sichtbar
  - [ ] Empty States sind sichtbar

---

## 🔒 Sicherheit

### ✅ Checklist: Sicherheit

- [ ] **1. API Key nicht im Code**
  - Nur in Environment Variables
  - Nicht in Git committen

- [ ] **2. CORS korrekt konfiguriert**
  - Railway: CORS_ORIGINS mit Lovable URL

- [ ] **3. HTTPS verwenden**
  - Railway: Automatisch HTTPS
  - Lovable: Automatisch HTTPS

---

## 📊 Monitoring

### ✅ Checklist: Monitoring

- [ ] **1. Railway Logs prüfen**
  - Logs → Siehe API Requests
  - Errors → Siehe Fehler

- [ ] **2. Lovable Console prüfen**
  - Browser DevTools → Console
  - Siehe API Errors

---

## 🎉 Fertig!

Wenn alle Checklisten abgehakt sind, hast du:

✅ CPA Server auf Railway deployed
✅ Admin Token generiert
✅ Lovable UI mit API verbunden
✅ Dashboard mit Agent-Karten
✅ Agent Detail mit Live Logs
✅ Screenshot Gallery

**Viel Erfolg!** 🚀

