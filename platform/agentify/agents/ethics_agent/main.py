"""Ethics Agent - FastAPI implementation.

ARCHITECTURAL EVOLUTION:
-----------------------
This agent demonstrates the transition from direct peer-to-peer communication
to orchestrator-mediated routing in the Agentify platform.

CURRENT IMPLEMENTATION (v1.0.0 - Standalone Mode):
  - Direct A2A communication with LLM agent via httpx
  - Configurable LLM_AGENT_URL for flexibility
  - Suitable for development and testing without full orchestrator

FUTURE IMPLEMENTATION (v2.0.0 - Orchestrated Mode):
  - Capability-based routing via Orchestrator Agent
  - Dynamic LLM agent discovery from marketplace
  - No hard-coded agent URLs - all discovered at runtime
  - Follows "Recursive System Architecture" principle

Key Design Principles:
  1. Separation of Concerns: Ethics logic separate from LLM execution
  2. Dependency Injection: LLM agent URL is configurable
  3. Graceful Degradation: Falls back to rule-based if LLM unavailable
  4. Standards Compliance: Full Agent Standard v1 + A2A protocol
  5. Future-Ready: Designed for easy migration to orchestrator routing

For architecture details, see:
  - platform/agentify/ARCHITECTURE.md
  - platform/agentify/orchestrator/README.md
  - platform/agentify/PLATFORM_ARCHITECTURE.md
"""
import sys
import os
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import uvicorn
import httpx

# Add base_orchestrator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "base_orchestrator"))

from base_orchestrator.models import AgentMessage, MessageType

app = FastAPI(title="Ethics Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvaluationRequest(BaseModel):
    agent_id: str
    action: str
    context: dict[str, Any]
    ethics_framework: str = "harm-minimization"


class EvaluationResponse(BaseModel):
    allowed: bool
    violations: list[str]
    recommendations: list[str]
    explanation: str


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "agent": "ethics", "version": "1.0.0"}


@app.get("/manifest")
async def get_manifest():
    """Return agent manifest."""
    manifest_path = Path(__file__).parent / "manifest.json"
    with open(manifest_path, "r") as f:
        return json.load(f)


@app.post("/agent/message")
async def agent_message(message: AgentMessage):
    """Handle Agent Communication Protocol messages."""
    
    print(f"\n📨 Received message:")
    print(f"   Type: {message.type}")
    print(f"   Sender: {message.sender}")
    print(f"   Intent: {message.intent}")
    print(f"   Payload: {message.payload}")
    
    # Route based on intent
    if message.intent == "evaluate_action":
        return await handle_evaluate_action(message)
    elif message.intent == "audit_decision":
        return await handle_audit_decision(message)
    elif message.intent == "check_health":
        return await handle_check_health(message)
    elif message.intent == "escalate_violation":
        return await handle_escalate_violation(message)
    else:
        return AgentMessage(
            type=MessageType.REFUSE,
            sender="agent.agentify.ethics",
            to=[message.sender],
            intent="unknown_intent",
            payload={"error": f"Unknown intent: {message.intent}"}
        )


async def handle_evaluate_action(message: AgentMessage) -> AgentMessage:
    """Evaluate an action against ethics framework using GPT Agent.
    
    ARCHITECTURAL NOTE:
    -------------------
    Current implementation uses direct A2A communication to an LLM agent.
    This is a transitional approach while the full Orchestrator Agent is being developed.
    
    CURRENT BEHAVIOR (v1.0.0):
    - Ethics Agent directly calls LLM agent via LLM_AGENT_URL
    - Uses Agent Communication Protocol for peer-to-peer communication
    - Falls back to rule-based evaluation if LLM unavailable
    
    FUTURE BEHAVIOR (v2.0.0 - when Orchestrator is ready):
    - Ethics Agent declares "I need NLP capability" to Orchestrator
    - Orchestrator discovers available LLM agents in team (GPT/Claude/Llama/etc.)
    - Orchestrator routes the request to best available LLM agent
    - Ethics Agent receives response without knowing which LLM was used
    
    This follows the "Recursive System Architecture" principle:
    - Each capability is discovered dynamically, not hard-coded
    - Marketplace can offer competing LLM agents (price/quality trade-offs)
    - True loose coupling between agents
    
    See: platform/agentify/ARCHITECTURE.md - Orchestrator Agent responsibilities
    See: platform/agentify/orchestrator/README.md - Dynamic team composition
    
    TODO (when Orchestrator Agent v1 is deployed):
    [ ] Remove direct LLM_AGENT_URL configuration
    [ ] Add capability declaration: {"required_capability": "llm.structured_completion"}
    [ ] Update to use orchestrator.route_message() instead of direct httpx call
    [ ] Let orchestrator handle LLM agent discovery and routing
    """
    
    payload = message.payload
    agent_id = payload.get("agent_id")
    action = payload.get("action")
    context = payload.get("context", {})
    framework = payload.get("ethics_framework", "harm-minimization")
    
    print(f"\n🔍 Evaluating action:")
    print(f"   Agent: {agent_id}")
    print(f"   Action: {action}")
    print(f"   Framework: {framework}")
    
    # TEMPORARY: Direct LLM agent call (v1.0.0)
    # This will be replaced by orchestrator routing in v2.0.0
    # The LLM_AGENT_URL can point to ANY LLM-capable agent (GPT, Claude, Llama, etc.)
    llm_agent_url = os.getenv("LLM_AGENT_URL", "http://localhost:8004")
    
    try:
        # Call GPT Agent via A2A protocol
        prompt = f"""You are an AI ethics evaluator following the {framework} framework.

Evaluate the following action for ethical concerns:

Agent: {agent_id}
Action: {action}
Context: {context}

Provide your evaluation in the following JSON format:
{{
  "allowed": true or false,
  "violations": ["list of any ethical violations"],
  "recommendations": ["list of recommendations"],
  "explanation": "brief explanation of your decision"
}}

Consider:
- Potential harm to users or systems
- Privacy and data protection
- Transparency and consent
- Fairness and non-discrimination
- Accountability and reversibility
"""
        
        gpt_message = AgentMessage(
            type=MessageType.REQUEST,
            sender="agent.agentify.ethics",
            to=["agent.agentify.gpt"],
            intent="structured_completion",
            payload={
                "prompt": prompt,
                "model": "gpt-4o-mini",
                "temperature": 0.3
            },
            context={
                "purpose": "ethics_evaluation",
                "target_agent": agent_id,
                "target_action": action,
                "framework": framework
            }
        )
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{llm_agent_url}/agent/message",
                json=gpt_message.model_dump(mode="json")
            )
            response.raise_for_status()
            gpt_response = AgentMessage(**response.json())
            
        if gpt_response.type == MessageType.INFORM:
            result = gpt_response.payload.get("result", {})
            allowed = result.get("allowed", False)
            violations = result.get("violations", [])
            recommendations = result.get("recommendations", [])
            explanation = result.get("explanation", "")
        else:
            print(f"⚠️  LLM Agent failed, falling back to rule-based")
            return await handle_evaluate_action_fallback(message)
                
    except Exception as e:
        print(f"⚠️  LLM Agent call failed: {e}, falling back to rule-based")
        return await handle_evaluate_action_fallback(message)
    
    result = {
        "allowed": allowed,
        "violations": violations,
        "recommendations": recommendations,
        "explanation": explanation
    }
    
    print(f"\n✅ Evaluation result: {'ALLOWED' if allowed else 'BLOCKED'}")
    if violations:
        print(f"   Violations: {violations}")
    if recommendations:
        print(f"   Recommendations: {recommendations}")
    
    return AgentMessage(
        type=MessageType.INFORM,
        sender="agent.agentify.ethics",
        to=[message.sender],
        intent="evaluation_result",
        payload=result
    )


async def handle_evaluate_action_fallback(message: AgentMessage) -> AgentMessage:
    """Fallback rule-based evaluation when LLM is unavailable."""
    
    payload = message.payload
    agent_id = payload.get("agent_id")
    action = payload.get("action")
    context = payload.get("context", {})
    
    violations = []
    recommendations = []
    
    # Simple keyword-based evaluation
    harmful_keywords = ["delete", "destroy", "harm", "kill", "attack"]
    action_lower = action.lower()
    
    for keyword in harmful_keywords:
        if keyword in action_lower:
            violations.append(f"Action contains harmful keyword: '{keyword}'")
    
    if not context.get("user_consent"):
        recommendations.append("Consider obtaining explicit user consent")
    
    allowed = len(violations) == 0
    explanation = "Action passed ethics evaluation (rule-based)" if allowed else "Action blocked due to ethics violations (rule-based)"
    
    result = {
        "allowed": allowed,
        "violations": violations,
        "recommendations": recommendations,
        "explanation": explanation
    }
    
    print(f"\n✅ Evaluation result (fallback): {'ALLOWED' if allowed else 'BLOCKED'}")
    if violations:
        print(f"   Violations: {violations}")
    if recommendations:
        print(f"   Recommendations: {recommendations}")
    
    return AgentMessage(
        type=MessageType.INFORM,
        sender="agent.agentify.ethics",
        to=[message.sender],
        intent="evaluation_result",
        payload=result
    )


async def handle_audit_decision(message: AgentMessage) -> AgentMessage:
    """Audit a decision after execution."""
    
    payload = message.payload
    agent_id = payload.get("agent_id")
    action = payload.get("action")
    result = payload.get("result", {})
    
    print(f"\n📋 Auditing decision:")
    print(f"   Agent: {agent_id}")
    print(f"   Action: {action}")
    print(f"   Result: {result}")
    
    # Simple audit logic
    issues = []
    recommendations = []
    
    if not result.get("success"):
        issues.append("Action failed - review error handling")
    
    if result.get("duration_ms", 0) > 5000:
        recommendations.append("Consider optimizing action performance")
    
    audit_result = {
        "compliant": len(issues) == 0,
        "issues": issues,
        "recommendations": recommendations
    }
    
    print(f"\n✅ Audit result: {'COMPLIANT' if len(issues) == 0 else 'ISSUES FOUND'}")
    
    return AgentMessage(
        type=MessageType.INFORM,
        sender="agent.agentify.ethics",
        to=[message.sender],
        intent="audit_result",
        payload=audit_result
    )


async def handle_check_health(message: AgentMessage) -> AgentMessage:
    """Check agent health based on desire profile."""
    
    payload = message.payload
    agent_id = payload.get("agent_id")
    
    print(f"\n🏥 Checking health:")
    print(f"   Agent: {agent_id}")
    
    # Mock health check
    health_result = {
        "health_state": "healthy",
        "tension_level": 0.3,
        "concerns": []
    }
    
    print(f"\n✅ Health status: {health_result['health_state']}")
    
    return AgentMessage(
        type=MessageType.INFORM,
        sender="agent.agentify.ethics",
        to=[message.sender],
        intent="health_status",
        payload=health_result
    )


async def handle_escalate_violation(message: AgentMessage) -> AgentMessage:
    """Escalate ethics violation to oversight."""
    
    payload = message.payload
    agent_id = payload.get("agent_id")
    violation = payload.get("violation")
    severity = payload.get("severity", "medium")
    
    print(f"\n⚠️  ESCALATING VIOLATION:")
    print(f"   Agent: {agent_id}")
    print(f"   Severity: {severity}")
    print(f"   Violation: {violation}")
    
    escalation_result = {
        "escalation_id": f"ESC-{agent_id}-{violation.get('id', 'unknown')}",
        "status": "escalated"
    }
    
    return AgentMessage(
        type=MessageType.INFORM,
        sender="agent.agentify.ethics",
        to=[message.sender],
        intent="escalation_complete",
        payload=escalation_result
    )


if __name__ == "__main__":
    port = 8003
    print(f"\n🚀 Starting Ethics Agent on http://localhost:{port}")
    print(f"📄 Manifest: manifest.json")
    print(f"🔍 Health: http://localhost:{port}/health")
    print(f"📡 Agent Protocol: http://localhost:{port}/agent/message\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
