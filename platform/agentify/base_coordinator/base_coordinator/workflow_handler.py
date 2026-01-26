"""Workflow Handler - A2A Workflow Chaining Protocol

This module provides workflow context propagation for true agent-to-agent handoffs.

Usage in any agent:
    from base_coordinator.workflow_handler import handle_workflow_chain
    
    # In your agent's message handler:
    if "__workflow__" in message.payload:
        return await handle_workflow_chain(
            message=message,
            my_result=my_computed_result,
            agent_id="agent.my.id"
        )
"""
import json
import httpx
from typing import Any
from datetime import datetime
from .models import AgentMessage, MessageType


async def handle_workflow_chain(
    message: AgentMessage,
    my_result: dict[str, Any],
    agent_id: str,
    http_client: httpx.AsyncClient | None = None
) -> AgentMessage:
    """Handle workflow chaining - call next agent or return to coordinator.
    
    Uses manifest I/O schemas + GPT to intelligently map data between agents.
    
    Args:
        message: Incoming A2A message with __workflow__ context
        my_result: This agent's result to pass to next agent
        agent_id: This agent's ID
        http_client: Optional HTTP client (creates new one if not provided)
        
    Returns:
        AgentMessage to send back (either to next agent or coordinator)
    """
    workflow = message.payload.get("__workflow__")
    if not workflow:
        # No workflow context, just return result normally
        return AgentMessage(
            type=MessageType.INFORM,
            sender=agent_id,
            to=[message.sender],
            intent="result",
            payload=my_result
        )
    
    # Extract workflow info
    current_step = workflow.get("current_step", 0)
    total_steps = workflow.get("total_steps", 0)
    steps = workflow.get("steps", [])
    trace = workflow.get("trace", [])
    
    # Add current step to trace
    step_info = {
        "step": current_step + 1,
        "agent": agent_id,
        "result": my_result,
        "timestamp": datetime.utcnow().isoformat(),
        "duration_ms": 0
    }
    trace.append(step_info)
    
    print(f"\n🔗 Workflow step {current_step + 1}/{total_steps} complete")
    print(f"   Result: {str(my_result)[:100]}...")
    
    # Check if this is the last step
    if current_step + 1 >= total_steps:
        # Last step - return to coordinator
        print(f"✅ Final step complete, returning to coordinator")
        return AgentMessage(
            type=MessageType.INFORM,
            sender=agent_id,
            to=[message.sender],
            intent="workflow_complete",
            payload={
                **my_result,
                "__workflow__": {
                    **workflow,
                    "trace": trace,
                    "completed": True
                }
            }
        )
    
    # Not the last step - call next agent
    next_step_idx = current_step + 1
    next_step = steps[next_step_idx]
    next_agent_id = next_step["agent_id"]
    next_agent_address = next_step["agent_address"]
    next_intent = next_step["intent"]
    next_params = next_step["params"].copy()
    
    print(f"➡️  Calling next agent: {next_agent_id}")
    
    # Fetch next agent's manifest to understand expected input
    close_client = False
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=120.0)
        close_client = True
    
    try:
        print(f"📄 Fetching manifest from {next_agent_address}/manifest")
        manifest_response = await http_client.get(f"{next_agent_address}/manifest")
        manifest_response.raise_for_status()
        next_manifest = manifest_response.json()
        
        # Extract I/O schema for the next intent
        next_io_schemas = next_manifest.get("io", {}).get("schemas", {})
        next_input_schema = next_io_schemas.get(next_intent, {}).get("input", {})
        
        if next_input_schema:
            print(f"🔍 Next agent expects: {list(next_input_schema.keys())}")
            print(f"   I have: {list(my_result.keys())}")
            
            # Use GPT to intelligently map my_result to next agent's expected input
            # Find GPT agent address from workflow
            gpt_address = None
            for step in steps:
                if "gpt" in step.get("agent_id", "").lower():
                    gpt_address = step.get("agent_address")
                    break
            
            if gpt_address:
                print(f"🧠 Using GPT to map output → input")
                mapping_prompt = f"""You are a data mapping expert. Map the output from one agent to the input expected by another agent.

MY OUTPUT:
{json.dumps(my_result, indent=2)}

NEXT AGENT EXPECTS (input schema for '{next_intent}'):
{json.dumps(next_input_schema, indent=2)}

ALREADY PROVIDED PARAMS:
{json.dumps(next_params, indent=2)}

Create a JSON mapping that extracts values from MY OUTPUT and assigns them to the parameters expected by the next agent.
Only map parameters that are NOT already provided.

Respond with ONLY valid JSON (no markdown):
{{
  "param_name": "path.to.value.in.my.output"
}}

Example:
- If next agent needs "value" and my output has {{"result": 123}}, return: {{"value": "result"}}
- If next agent needs "text" and my output has {{"data": {{"content": "hello"}}}}, return: {{"text": "data.content"}}
"""
                
                try:
                    gpt_response = await http_client.post(
                        f"{gpt_address}/agent/message",
                        json=AgentMessage(
                            type=MessageType.REQUEST,
                            sender=agent_id,
                            to=["agent.agentify.gpt"],
                            intent="structured_completion",
                            payload={
                                "prompt": mapping_prompt,
                                "model": "gpt-4o-mini",
                                "temperature": 0.1
                            }
                        ).model_dump(mode="json")
                    )
                    gpt_response.raise_for_status()
                    gpt_result = gpt_response.json()
                    mapping = gpt_result.get("payload", {}).get("result", {})
                    
                    if mapping:
                        print(f"   GPT mapping: {mapping}")
                        # Apply the mapping
                        for param_name, json_path in mapping.items():
                            if param_name not in next_params:
                                # Extract value using JSON path
                                value = my_result
                                for key in json_path.split("."):
                                    if isinstance(value, dict) and key in value:
                                        value = value[key]
                                    else:
                                        break
                                next_params[param_name] = value
                                print(f"   ✓ Mapped {param_name} = {value}")
                except Exception as e:
                    print(f"   ⚠️  GPT mapping failed: {e}, using fallback")
                    # Fallback: simple direct mapping
                    for param_name in next_input_schema.keys():
                        if param_name not in next_params:
                            if param_name in my_result:
                                next_params[param_name] = my_result[param_name]
                            elif "result" in my_result and isinstance(my_result["result"], (int, float, str)):
                                if param_name == "value":
                                    next_params[param_name] = my_result["result"]
            else:
                # No GPT available, use simple fallback
                print(f"   ⚠️  No GPT agent, using simple mapping")
                for param_name in next_input_schema.keys():
                    if param_name not in next_params:
                        if param_name in my_result:
                            next_params[param_name] = my_result[param_name]
                        elif "result" in my_result and isinstance(my_result["result"], (int, float, str)):
                            if param_name == "value":
                                next_params[param_name] = my_result["result"]
        
        # Update workflow context
        updated_workflow = {
            **workflow,
            "current_step": next_step_idx,
            "trace": trace,
            "previous_result": my_result
        }
        
        # Call next agent
        print(f"📤 Delegating to {next_agent_address}")
        response = await http_client.post(
            f"{next_agent_address}/agent/message",
            json=AgentMessage(
                type=MessageType.REQUEST,
                sender=agent_id,
                to=[next_agent_id],
                intent=next_intent,
                payload={
                    **next_params,
                    "__workflow__": updated_workflow
                }
            ).model_dump(mode="json")
        )
        response.raise_for_status()
        
        # Return the response from next agent (it will eventually come back)
        next_result = response.json()
        
        # The final response will bubble back through the chain
        return AgentMessage(**next_result)
        
    finally:
        if close_client:
            await http_client.aclose()
