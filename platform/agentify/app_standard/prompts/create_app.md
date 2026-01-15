# 🚀 Create Agentify App - AI Prompt

**Use this prompt with Lovable, Cursor, Copilot, Augment, v0, or Bolt to generate a complete Agentify app**

---

## 📋 **Prompt**

Copy and paste this prompt into your AI tool:

```
Create a complete Agentify-compliant React application with the following specifications:

## App Details
- App Name: {APP_NAME}
- Description: {APP_DESCRIPTION}
- Required Agent Capabilities: {CAPABILITIES}

## Technology Stack
- Framework: Vite + React 18+ (TypeScript)
- Styling: Tailwind CSS
- State Management: Zustand
- Routing: React Router v6
- UI Components: shadcn/ui (Tailwind-based)
- Icons: Lucide React
- HTTP Client: Axios

## Project Structure
```
my-app/
├── public/
│   └── agentify.json              # App manifest
├── src/
│   ├── agents/
│   │   └── orchestrator/
│   │       ├── manifest.json      # Orchestrator manifest
│   │       ├── orchestrator.ts    # Orchestrator implementation
│   │       └── tools/             # Orchestrator tools
│   │           ├── MarketplaceQuery.ts
│   │           └── TeamBuilder.ts
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Standalone.tsx     # Standalone layout
│   │   │   ├── Integrated.tsx     # Integrated layout (sidebar + main)
│   │   │   └── Sidebar.tsx        # Sidebar component
│   │   ├── team/
│   │   │   ├── TeamBuilder.tsx    # Team building UI
│   │   │   ├── AgentCard.tsx      # Agent display card
│   │   │   └── TeamList.tsx       # Current team list
│   │   └── ui/                    # shadcn/ui components
│   ├── stores/
│   │   ├── appStore.ts            # App state (Zustand)
│   │   └── agentStore.ts          # Agent team state (Zustand)
│   ├── services/
│   │   ├── marketplace.ts         # Marketplace API client
│   │   ├── dataSharing.ts         # Data sharing API client
│   │   ├── orchestrator.ts        # Orchestrator service
│   │   └── storage.ts             # Storage abstraction
│   ├── types/
│   │   ├── agent.ts               # Agent types
│   │   ├── app.ts                 # App types
│   │   └── team.ts                # Team types
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Required Files

### 1. App Manifest (public/agentify.json)
```json
{
  "app_id": "app.company.{APP_ID}",
  "name": "{APP_NAME}",
  "version": "1.0.0",
  "description": "{APP_DESCRIPTION}",
  "author": {
    "name": "Your Company",
    "email": "dev@company.com"
  },
  "orchestrator": {
    "manifest_path": "/src/agents/orchestrator/manifest.json",
    "enabled": true
  },
  "modes": {
    "standalone": true,
    "integrated": true
  },
  "data_sharing": {
    "enabled": true,
    "resources": []
  },
  "marketplace": {
    "url": "https://marketplace.agentify.io",
    "auto_register": true
  },
  "storage": {
    "default": "cloud",
    "options": ["cloud", "edge", "local"],
    "configurable": true
  }
}
```

### 2. Orchestrator Manifest (src/agents/orchestrator/manifest.json)
```json
{
  "agent_id": "agent.{APP_ID}.orchestrator",
  "name": "{APP_NAME} Orchestrator",
  "version": "1.0.0",
  "status": "active",
  "ethics": {
    "framework": "harm-minimization",
    "hard_constraints": [
      "no_unauthorized_team_changes",
      "no_budget_overrun"
    ]
  },
  "desires": {
    "profile": [
      {"id": "team_efficiency", "weight": 0.4},
      {"id": "cost_optimization", "weight": 0.3},
      {"id": "user_satisfaction", "weight": 0.3}
    ]
  },
  "tools": [
    {
      "name": "query_marketplace",
      "description": "Query marketplace for agents",
      "category": "discovery"
    },
    {
      "name": "build_team",
      "description": "Build team from agents",
      "category": "orchestration"
    }
  ],
  "authority": {
    "instruction": {"type": "app", "id": "app.{APP_ID}"},
    "oversight": {"type": "human", "id": "user", "independent": true}
  }
}
```

### 3. App Store (src/stores/appStore.ts)
```typescript
import { create } from 'zustand';

interface AppState {
  mode: 'standalone' | 'integrated';
  user: User | null;
  setMode: (mode: 'standalone' | 'integrated') => void;
  setUser: (user: User | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  mode: 'standalone',
  user: null,
  setMode: (mode) => set({ mode }),
  setUser: (user) => set({ user }),
}));
```

### 4. Agent Store (src/stores/agentStore.ts)
```typescript
import { create } from 'zustand';
import { Agent, Team } from '../types/agent';

interface AgentState {
  team: Agent[];
  orchestrator: any | null;
  addAgent: (agent: Agent) => void;
  removeAgent: (agentId: string) => void;
  setOrchestrator: (orchestrator: any) => void;
}

export const useAgentStore = create<AgentState>((set) => ({
  team: [],
  orchestrator: null,
  addAgent: (agent) => set((state) => ({ team: [...state.team, agent] })),
  removeAgent: (agentId) => set((state) => ({
    team: state.team.filter((a) => a.agent_id !== agentId)
  })),
  setOrchestrator: (orchestrator) => set({ orchestrator }),
}));
```

### 5. Marketplace Service (src/services/marketplace.ts)
```typescript
import axios from 'axios';
import { Agent } from '../types/agent';

const MARKETPLACE_URL = 'https://marketplace.agentify.io/api';

export class MarketplaceService {
  async searchAgents(requirements: {
    capabilities: string[];
    maxPrice?: number;
    minRating?: number;
  }): Promise<Agent[]> {
    const response = await axios.post(`${MARKETPLACE_URL}/search`, {
      requirements
    });
    return response.data;
  }

  async bookAgent(agentId: string, teamId: string): Promise<void> {
    await axios.post(`${MARKETPLACE_URL}/book`, {
      agent_id: agentId,
      team_id: teamId
    });
  }
}

export const marketplaceService = new MarketplaceService();
```

### 6. Layouts

**Standalone Layout (src/components/layout/Standalone.tsx):**
```typescript
import { Outlet } from 'react-router-dom';

export function StandaloneLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">{APP_NAME}</h1>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
```

**Integrated Layout (src/components/layout/Integrated.tsx):**
```typescript
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function IntegratedLayout() {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-gray-900 text-white">
        <Sidebar />
      </aside>
      <main className="flex-1 bg-gray-50">
        <header className="bg-white shadow px-6 py-4">
          <h1 className="text-2xl font-bold">{APP_NAME}</h1>
        </header>
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
```

## Features to Implement

1. **Team Building UI**
   - Search agents by capability
   - Display agent cards (name, rating, price)
   - Human-in-the-loop approval before booking
   - Current team display

2. **Mode Switcher**
   - Toggle between standalone and integrated modes
   - Persist mode preference

3. **Orchestrator Integration**
   - Initialize orchestrator on app load
   - Query marketplace via orchestrator
   - Build teams via orchestrator

4. **Responsive Design**
   - Mobile-friendly
   - Tailwind CSS utilities
   - Dark mode support (optional)

## Additional Requirements

- Use TypeScript for all files
- Include proper error handling
- Add loading states for async operations
- Include basic form validation
- Follow Agentify App Standard v1 specification
- Ensure all components are accessible (ARIA labels)

## Expected Output

Generate a complete, working Agentify app with:
- All files in the project structure
- Working orchestrator integration
- Team building UI
- Both standalone and integrated layouts
- Proper TypeScript types
- Tailwind CSS styling
- Zustand state management

The app should be ready to run with `npm install && npm run dev`.
```

---

## 🎯 **Customization**

Replace these placeholders:

- `{APP_NAME}` - Your app name (e.g., "Email Manager")
- `{APP_DESCRIPTION}` - What your app does (e.g., "Manages email campaigns")
- `{APP_ID}` - Unique app ID (e.g., "email-manager")
- `{CAPABILITIES}` - Required capabilities (e.g., "email_sending, scheduling")

---

## 📝 **Example**

```
Create a complete Agentify-compliant React application with the following specifications:

## App Details
- App Name: Email Campaign Manager
- Description: Manage and automate email marketing campaigns
- Required Agent Capabilities: email_sending, scheduling, analytics

[... rest of prompt ...]
```

---

## ✅ **Verification**

After generation, verify:

1. ✅ All files created
2. ✅ `npm install` works
3. ✅ `npm run dev` starts the app
4. ✅ Both layouts render correctly
5. ✅ Orchestrator initializes
6. ✅ Marketplace integration works

---

**Next:** Test your app and iterate with additional prompts!

