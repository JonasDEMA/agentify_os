/**
 * Agent UI Template - Agentify Platform
 * 
 * Complete UI template for displaying agent information with all 14 manifest sections
 * Includes Ethics, Desires, Health, Tools, Memory, and more
 * 
 * Usage: Copy this template and customize for your agent UI
 */

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Activity, 
  AlertTriangle, 
  Brain, 
  Calendar, 
  CheckCircle, 
  Clock, 
  Code, 
  Database, 
  DollarSign, 
  Eye, 
  FileText, 
  Heart, 
  Info, 
  Lock, 
  MessageSquare, 
  Settings, 
  Shield, 
  Users, 
  Zap 
} from 'lucide-react';

// Agent Manifest Type (simplified - use your actual types)
interface AgentManifest {
  agent_id: string;
  name: string;
  version: string;
  status: 'draft' | 'active' | 'paused' | 'retired';
  overview: {
    description: string;
    tags: string[];
    owner: { name: string };
  };
  capabilities: Array<{ name: string; level: string }>;
  ai_model?: { provider: string; model: string };
  ethics: {
    framework: string;
    hard_constraints: string[];
    soft_constraints: string[];
  };
  desires: {
    profile: Array<{ id: string; weight: number; satisfaction: number }>;
  };
  health?: {
    state: 'healthy' | 'stressed' | 'degraded' | 'critical';
    tension: number;
  };
  pricing?: {
    model: string;
    per_request: number;
    currency: string;
  };
  tools: Array<{
    name: string;
    description: string;
    connection?: { status: string };
  }>;
  memory?: {
    slots: Array<{ name: string; type: string }>;
  };
  schedule?: {
    jobs: Array<{ name: string; cron: string; enabled: boolean }>;
  };
  activities?: {
    queue: Array<{ id: string; status: string }>;
  };
  team?: {
    relationships: Array<{ agent_id: string; relationship: string }>;
  };
  customers?: {
    assignments: Array<{ customer_id: string; load: any }>;
  };
  knowledge?: {
    rag?: { datasets: Array<{ name: string }> };
  };
  io: {
    input_formats: string[];
    output_formats: string[];
  };
  revisions: {
    current_revision: string;
    history: Array<{ revision_id: string; timestamp: string; change_summary: string }>;
  };
  authority: {
    instruction: { id: string };
    oversight: { id: string };
  };
  observability?: {
    incidents: Array<{ severity: string; message: string }>;
  };
}

export function AgentUI({ manifest }: { manifest: AgentManifest }) {
  const [activeTab, setActiveTab] = useState('overview');

  // Health color mapping
  const healthColors = {
    healthy: 'text-green-500',
    stressed: 'text-yellow-500',
    degraded: 'text-orange-500',
    critical: 'text-red-500',
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="w-8 h-8" />
            {manifest.name}
          </h1>
          <p className="text-muted-foreground">{manifest.agent_id}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={manifest.status === 'active' ? 'default' : 'secondary'}>
            {manifest.status}
          </Badge>
          <Badge variant="outline">v{manifest.version}</Badge>
          {manifest.health && (
            <Badge className={healthColors[manifest.health.state]}>
              <Heart className="w-4 h-4 mr-1" />
              {manifest.health.state}
            </Badge>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid grid-cols-7 lg:grid-cols-14 gap-1">
          <TabsTrigger value="overview"><Info className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="ethics"><Shield className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="pricing"><DollarSign className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="tools"><Zap className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="memory"><Database className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="schedule"><Calendar className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="activities"><Activity className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="prompt"><MessageSquare className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="team"><Users className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="customers"><Users className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="knowledge"><FileText className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="io"><Code className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="revisions"><Clock className="w-4 h-4" /></TabsTrigger>
          <TabsTrigger value="authority"><Eye className="w-4 h-4" /></TabsTrigger>
        </TabsList>

        {/* Tab 1: Overview */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="w-5 h-5" />
                Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Description</h3>
                <p className="text-muted-foreground">{manifest.overview.description}</p>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {manifest.overview.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">{tag}</Badge>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Capabilities</h3>
                <div className="grid grid-cols-2 gap-2">
                  {manifest.capabilities.map((cap) => (
                    <div key={cap.name} className="flex items-center justify-between p-2 border rounded">
                      <span>{cap.name}</span>
                      <Badge variant="outline">{cap.level}</Badge>
                    </div>
                  ))}
                </div>
              </div>

              {manifest.ai_model && (
                <div>
                  <h3 className="font-semibold mb-2">AI Model</h3>
                  <p className="text-muted-foreground">
                    {manifest.ai_model.provider} / {manifest.ai_model.model}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Ethics & Desires */}
        <TabsContent value="ethics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Ethics & Desires
              </CardTitle>
              <CardDescription>Runtime-active ethics and health monitoring</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Ethics */}
              <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Shield className="w-4 h-4" />
                  Ethics Framework: {manifest.ethics.framework}
                </h3>
                
                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium mb-2">Hard Constraints (BLOCKING)</h4>
                    <div className="space-y-1">
                      {manifest.ethics.hard_constraints.map((constraint) => (
                        <Alert key={constraint} variant="destructive">
                          <AlertTriangle className="w-4 h-4" />
                          <AlertDescription>{constraint}</AlertDescription>
                        </Alert>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-medium mb-2">Soft Constraints (WARNING)</h4>
                    <div className="space-y-1">
                      {manifest.ethics.soft_constraints.map((constraint) => (
                        <Alert key={constraint}>
                          <Info className="w-4 h-4" />
                          <AlertDescription>{constraint}</AlertDescription>
                        </Alert>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Desires */}
              <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Heart className="w-4 h-4" />
                  Desire Profile
                </h3>
                <div className="space-y-3">
                  {manifest.desires.profile.map((desire) => (
                    <div key={desire.id} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium">{desire.id}</span>
                        <span className="text-muted-foreground">
                          Weight: {(desire.weight * 100).toFixed(0)}% | 
                          Satisfaction: {(desire.satisfaction * 100).toFixed(0)}%
                        </span>
                      </div>
                      <Progress value={desire.satisfaction * 100} />
                    </div>
                  ))}
                </div>
              </div>

              {/* Health */}
              {manifest.health && (
                <div>
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    Health State
                  </h3>
                  <Alert className={healthColors[manifest.health.state]}>
                    <Heart className="w-4 h-4" />
                    <AlertDescription>
                      <div className="flex items-center justify-between">
                        <span className="font-semibold">{manifest.health.state.toUpperCase()}</span>
                        <span>Tension: {(manifest.health.tension * 100).toFixed(1)}%</span>
                      </div>
                    </AlertDescription>
                  </Alert>
                  <Progress value={manifest.health.tension * 100} className="mt-2" />
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Pricing */}
        <TabsContent value="pricing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                Pricing
              </CardTitle>
            </CardHeader>
            <CardContent>
              {manifest.pricing ? (
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="font-medium">Model:</span>
                    <span>{manifest.pricing.model}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Per Request:</span>
                    <span>{manifest.pricing.per_request} {manifest.pricing.currency}</span>
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">No pricing configured</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 4: Tools */}
        <TabsContent value="tools" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Tools ({manifest.tools.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {manifest.tools.map((tool) => (
                  <div key={tool.name} className="flex items-center justify-between p-3 border rounded">
                    <div>
                      <p className="font-medium">{tool.name}</p>
                      <p className="text-sm text-muted-foreground">{tool.description}</p>
                    </div>
                    {tool.connection && (
                      <Badge variant={tool.connection.status === 'connected' ? 'default' : 'secondary'}>
                        {tool.connection.status}
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Add remaining tabs similarly... */}
        {/* Tab 5-14: Memory, Schedule, Activities, Prompt, Team, Customers, Knowledge, I/O, Revisions, Authority */}
        
      </Tabs>
    </div>
  );
}

export default AgentUI;

