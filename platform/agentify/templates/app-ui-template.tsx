/**
 * App UI Template - Agentify Platform
 * 
 * Complete UI template for Agentify-compliant React apps
 * Includes Marketplace integration, Team building, and Orchestrator UI
 * 
 * Usage: Copy this template and customize for your app
 */

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Bot, 
  Search, 
  Users, 
  Zap, 
  Settings, 
  Activity,
  Plus,
  Trash2,
  Play,
  Pause
} from 'lucide-react';

// Types
interface Agent {
  agent_id: string;
  name: string;
  capabilities: string[];
  pricing: { per_request: number; currency: string };
  rating: number;
  status: 'available' | 'busy' | 'offline';
}

interface TeamMember {
  agent: Agent;
  role: string;
  status: 'active' | 'paused';
}

export function AgentifyApp() {
  const [searchQuery, setSearchQuery] = useState('');
  const [team, setTeam] = useState<TeamMember[]>([]);
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([
    {
      agent_id: 'agent.company.email',
      name: 'Email Agent',
      capabilities: ['send_email', 'read_email'],
      pricing: { per_request: 0.01, currency: 'USD' },
      rating: 4.5,
      status: 'available',
    },
    // Add more agents...
  ]);

  const addToTeam = (agent: Agent, role: string) => {
    setTeam([...team, { agent, role, status: 'active' }]);
  };

  const removeFromTeam = (agentId: string) => {
    setTeam(team.filter(m => m.agent.agent_id !== agentId));
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Bot className="w-8 h-8" />
            My Agentify App
          </h1>
          <p className="text-muted-foreground">Build your agent team</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline">
            <Users className="w-4 h-4 mr-1" />
            {team.length} agents
          </Badge>
          <Button variant="outline" size="sm">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      <Tabs defaultValue="marketplace" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="marketplace">
            <Search className="w-4 h-4 mr-2" />
            Marketplace
          </TabsTrigger>
          <TabsTrigger value="team">
            <Users className="w-4 h-4 mr-2" />
            My Team
          </TabsTrigger>
          <TabsTrigger value="activity">
            <Activity className="w-4 h-4 mr-2" />
            Activity
          </TabsTrigger>
        </TabsList>

        {/* Marketplace Tab */}
        <TabsContent value="marketplace" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agent Marketplace</CardTitle>
              <CardDescription>Discover and add agents to your team</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Search */}
              <div className="flex gap-2">
                <Input
                  placeholder="Search agents by capability..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1"
                />
                <Button>
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </Button>
              </div>

              {/* Agent List */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availableAgents.map((agent) => (
                  <Card key={agent.agent_id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{agent.name}</CardTitle>
                        <Badge variant={agent.status === 'available' ? 'default' : 'secondary'}>
                          {agent.status}
                        </Badge>
                      </div>
                      <CardDescription>{agent.agent_id}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <p className="text-sm font-medium mb-2">Capabilities:</p>
                        <div className="flex flex-wrap gap-1">
                          {agent.capabilities.map((cap) => (
                            <Badge key={cap} variant="outline" className="text-xs">
                              {cap}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          {agent.pricing.per_request} {agent.pricing.currency}/request
                        </span>
                        <span className="text-sm">⭐ {agent.rating}</span>
                      </div>
                      <Button 
                        className="w-full" 
                        onClick={() => addToTeam(agent, 'member')}
                        disabled={team.some(m => m.agent.agent_id === agent.agent_id)}
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Add to Team
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Team Tab */}
        <TabsContent value="team" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>My Agent Team</CardTitle>
              <CardDescription>Manage your active agents</CardDescription>
            </CardHeader>
            <CardContent>
              {team.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No agents in your team yet</p>
                  <p className="text-sm">Add agents from the Marketplace</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {team.map((member) => (
                    <div key={member.agent.agent_id} className="flex items-center justify-between p-4 border rounded">
                      <div className="flex-1">
                        <p className="font-medium">{member.agent.name}</p>
                        <p className="text-sm text-muted-foreground">{member.role}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={member.status === 'active' ? 'default' : 'secondary'}>
                          {member.status}
                        </Badge>
                        <Button variant="outline" size="sm">
                          {member.status === 'active' ? (
                            <Pause className="w-4 h-4" />
                          ) : (
                            <Play className="w-4 h-4" />
                          )}
                        </Button>
                        <Button 
                          variant="destructive" 
                          size="sm"
                          onClick={() => removeFromTeam(member.agent.agent_id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Activity Tab */}
        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Activity Log</CardTitle>
              <CardDescription>Recent agent activities</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground text-center py-8">No recent activity</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default AgentifyApp;

