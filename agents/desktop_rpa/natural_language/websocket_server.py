"""WebSocket server for natural language agent communication.

This server:
1. Accepts WebSocket connections from the test UI
2. Receives natural language commands from user
3. Forwards to NaturalLanguageOrchestrator
4. Streams real-time updates back to UI
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import websockets
from websockets.server import WebSocketServerProtocol
import structlog

from agents.desktop_rpa.natural_language.nl_orchestrator import NaturalLanguageOrchestrator

logger = structlog.get_logger()


class WebSocketServer:
    """WebSocket server for agent communication."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """Initialize WebSocket server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        self.host = host
        self.port = port
        self.clients: set[WebSocketServerProtocol] = set()
        
        logger.info(f"WebSocket server initialized: {host}:{port}")
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a client connection.
        
        Args:
            websocket: WebSocket connection
            path: Request path
        """
        # Register client
        self.clients.add(websocket)
        client_id = id(websocket)
        logger.info(f"Client connected: {client_id}")
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                "message_type": "system_status",
                "status": "online",
                "message": "Connected to CPA Agent",
            }))
            
            # Create orchestrator with callback to send messages to this client
            def message_callback(message: dict[str, Any]):
                """Send message to client."""
                asyncio.create_task(websocket.send(json.dumps(message)))
            
            orchestrator = NaturalLanguageOrchestrator(
                message_callback=message_callback,
                use_vision=True,
                use_window_manager=True,
            )
            
            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get("message_type")
                    
                    if message_type == "user_command":
                        command = data.get("command")
                        if command:
                            logger.info(f"Received command from {client_id}: {command}")
                            
                            # Process command (runs in background)
                            asyncio.create_task(orchestrator.process_command(command))
                        else:
                            logger.warning(f"Empty command from {client_id}")
                    
                    else:
                        logger.warning(f"Unknown message type from {client_id}: {message_type}")
                
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from {client_id}: {e}")
                except Exception as e:
                    logger.error(f"Error processing message from {client_id}: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        
        finally:
            # Unregister client
            self.clients.discard(websocket)
    
    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"WebSocket server running on ws://{self.host}:{self.port}")
            print(f"\n🚀 WebSocket server running on ws://{self.host}:{self.port}")
            print(f"📱 Open test_ui.html in your browser to connect\n")
            
            # Run forever
            await asyncio.Future()  # Run forever


async def main():
    """Main entry point."""
    server = WebSocketServer(host="localhost", port=8765)
    await server.start()


if __name__ == "__main__":
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    
    # Run server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

