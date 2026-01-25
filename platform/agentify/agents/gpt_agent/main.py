"""GPT Agent - Generic LLM wrapper.

SECURITY & ETHICS ARCHITECTURE:
-------------------------------
This agent is a TOOL, not a decision-maker.

WHY NO PRE-ETHICS CHECK:
  - Ethics Agent uses this LLM agent to evaluate ethics (would be circular)
  - Calling agents (e.g., Ethics Agent) are responsible for ethical evaluation
  - This agent logs all calls for audit trails
  - OpenAI's safety layer provides base protection
  - Future: Multiple LLM providers will compete on safety

RESPONSIBILITY MODEL:
  - Requester is responsible for ethical use
  - This agent provides transparent execution logs
  - Audit trail includes: who, what, when, why
  - Oversight authority can review all generations

LOGGING FOR SECURITY (Doc 07, Section 6):
  - Who requested generation? → Logged via message.sender
  - For what purpose? → Logged via message.context.purpose
  - Was ethics check performed? → Logged if context includes ethics_evaluation
  - Token usage → Logged for cost/abuse monitoring

See: 07_Agentic_Economy_Security_Ethics_Architecture.docx
"""
import sys
import os
import json
import base64
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import uvicorn
import openai
import PyPDF2
import io

# Add base_coordinator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "base_coordinator"))

from base_coordinator.models import AgentMessage, MessageType

app = FastAPI(title="GPT Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    api_key_configured = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "ok",
        "agent": "gpt",
        "version": "1.0.0",
        "api_key_configured": api_key_configured
    }


@app.get("/manifest")
async def get_manifest():
    """Return agent manifest."""
    manifest_path = Path(__file__).parent / "manifest.json"
    with open(manifest_path, "r") as f:
        return json.load(f)


@app.post("/agent/message")
async def agent_message(message: AgentMessage):
    """Handle Agent Communication Protocol messages."""
    
    # Enhanced logging for security and audit trails
    print(f"\n📨 Received message:")
    print(f"   Type: {message.type}")
    print(f"   Sender: {message.sender}")
    print(f"   Intent: {message.intent}")
    print(f"   Message ID: {message.id}")
    print(f"   Timestamp: {message.ts}")
    
    # Log request context for audit trail
    context_info = {
        "requester": message.sender,
        "intent": message.intent,
        "message_id": message.id,
        "timestamp": str(message.ts),
        "correlation": message.correlation
    }
    print(f"   Context: {context_info}")
    
    # Route based on intent
    if message.intent == "chat_completion":
        return await handle_chat_completion(message)
    elif message.intent == "structured_completion":
        return await handle_structured_completion(message)
    elif message.intent == "analyze_image":
        return await handle_analyze_image(message)
    elif message.intent == "process_document":
        return await handle_process_document(message)
    else:
        return AgentMessage(
            type=MessageType.REFUSE,
            sender="agent.agentify.gpt",
            to=[message.sender],
            intent="unknown_intent",
            payload={"error": f"Unknown intent: {message.intent}"}
        )


async def handle_chat_completion(message: AgentMessage) -> AgentMessage:
    """Handle chat completion request."""
    
    payload = message.payload
    messages = payload.get("messages", [])
    model = payload.get("model", "gpt-4o-mini")
    temperature = payload.get("temperature", 0.7)
    max_tokens = payload.get("max_tokens", 1000)
    
    # Enhanced audit logging
    print(f"\n💬 Chat completion:")
    print(f"   Model: {model}")
    print(f"   Messages: {len(messages)}")
    print(f"   Requester: {message.sender}")
    print(f"   Purpose: {message.context.get('purpose', 'not specified')}")
    print(f"   Message ID: {message.id}")
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        result = {
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "model": response.model
        }
        
        # Log completion for audit trail
        print(f"✅ Completed: {result['usage']['total_tokens']} tokens")
        print(f"   Requester: {message.sender}")
        print(f"   Request ID: {message.id}")
        
        return AgentMessage(
            type=MessageType.INFORM,
            sender="agent.agentify.gpt",
            to=[message.sender],
            intent="completion_result",
            payload=result
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return AgentMessage(
            type=MessageType.FAILURE,
            sender="agent.agentify.gpt",
            to=[message.sender],
            intent="completion_failed",
            payload={"error": str(e)}
        )


async def handle_structured_completion(message: AgentMessage) -> AgentMessage:
    """Handle structured JSON completion request."""
    
    payload = message.payload
    prompt = payload.get("prompt", "")
    model = payload.get("model", "gpt-4o-mini")
    temperature = payload.get("temperature", 0.3)
    
    # Enhanced audit logging
    print(f"\n📋 Structured completion:")
    print(f"   Model: {model}")
    print(f"   Prompt length: {len(prompt)}")
    print(f"   Requester: {message.sender}")
    print(f"   Purpose: {message.context.get('purpose', 'not specified')}")
    print(f"   Message ID: {message.id}")
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        result_obj = json.loads(response.choices[0].message.content)
        
        result = {
            "result": result_obj,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
        # Log completion for audit trail
        print(f"✅ Completed: {result['usage']['total_tokens']} tokens")
        print(f"   Requester: {message.sender}")
        print(f"   Request ID: {message.id}")
        
        return AgentMessage(
            type=MessageType.INFORM,
            sender="agent.agentify.gpt",
            to=[message.sender],
            intent="structured_result",
            payload=result
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return AgentMessage(
            type=MessageType.FAILURE,
            sender="agent.agentify.gpt",
            to=[message.sender],
            intent="completion_failed",
            payload={"error": str(e)}
        )


if __name__ == "__main__":
    port = 8004
    print(f"\n🚀 Starting GPT Agent on http://localhost:{port}")
    print(f"📄 Manifest: manifest.json")
    print(f"🔍 Health: http://localhost:{port}/health")
    print(f"📡 Agent Protocol: http://localhost:{port}/agent/message\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)


async def handle_analyze_image(message: AgentMessage) -> AgentMessage:
    """Handle image analysis request."""
    payload = message.payload
    image_url = payload.get("image_url")
    image_base64 = payload.get("image_base64")
    prompt = payload.get("prompt", "Describe this image in detail.")
    model = payload.get("model", "gpt-4o")
    
    print(f"\n🖼️ Image analysis: Model={model}")
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        client = openai.OpenAI(api_key=api_key)
        
        if image_url:
            image_content = {"type": "image_url", "image_url": {"url": image_url}}
        elif image_base64:
            image_content = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        else:
            raise ValueError("Either image_url or image_base64 required")
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, image_content]}],
            max_tokens=1000
        )
        
        result = {
            "description": response.choices[0].message.content,
            "usage": {"total_tokens": response.usage.total_tokens}
        }
        
        return AgentMessage(
            type=MessageType.INFORM,
            sender="agent.agentify.gpt",
            to=[message.sender],
            intent="image_analysis_result",
            payload=result
        )
    except Exception as e:
        return AgentMessage(
            type=MessageType.FAILURE,
            sender="agent.agentify.gpt",
            to=[message.sender],
            intent="image_analysis_failed",
            payload={"error": str(e)}
        )


async def handle_process_document(message: AgentMessage) -> AgentMessage:
    """Handle document processing request."""
    payload = message.payload
    document_content = payload.get("document_content", "")
    document_type = payload.get("document_type", "txt")
    analysis_prompt = payload.get("analysis_prompt", "Summarize this document.")
    
    print(f"\n📄 Document processing: Type={document_type}")
    
    try:
        extracted_text = ""
        
        if document_type == "pdf":
            pdf_bytes = base64.b64decode(document_content)
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
        else:
            try:
                extracted_text = base64.b64decode(document_content).decode('utf-8')
            except:
                extracted_text = document_content
        
        analysis = ""
        if analysis_prompt and extracted_text:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"{analysis_prompt}\n\n{extracted_text[:10000]}"}],
                    temperature=0.3
                )
                analysis = response.choices[0].message.content
        
        result = {
            "extracted_text": extracted_text[:5000],
            "full_text_length": len(extracted_text),
            "analysis": analysis
        }
        
        return AgentMessage(
            type=MessageType.INFORM,
            sender="agent.agentify.gpt",
            to=[message.sender],
            intent="document_processed",
            payload=result
        )
    except Exception as e:
        return AgentMessage(
            type=MessageType.FAILURE,
            sender="agent.agentify.gpt",
            to=[message.sender],
            intent="document_processing_failed",
            payload={"error": str(e)}
        )
