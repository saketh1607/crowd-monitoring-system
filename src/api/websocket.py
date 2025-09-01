"""
WebSocket manager for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.router = APIRouter()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup WebSocket routes"""
        
        @self.router.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.connect(websocket)
            try:
                while True:
                    # Keep connection alive and handle incoming messages
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self.handle_message(websocket, message)
            except WebSocketDisconnect:
                self.disconnect(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.disconnect(websocket)
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": "Connected to Emergency Management System",
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def handle_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get("type")
            
            if message_type == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            
            elif message_type == "subscribe":
                # Handle subscription to specific event types
                await websocket.send_text(json.dumps({
                    "type": "subscription_confirmed",
                    "subscribed_to": message.get("events", []),
                    "timestamp": datetime.utcnow().isoformat()
                }))
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
        
        logger.info(f"Broadcasted message to {len(self.active_connections)} connections")
    
    async def broadcast_emergency_alert(self, emergency_data: Dict[str, Any]):
        """Broadcast emergency alert with high priority"""
        alert_message = {
            "type": "emergency_alert",
            "priority": "high",
            "data": emergency_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(alert_message)
    
    async def broadcast_status_update(self, status_data: Dict[str, Any]):
        """Broadcast system status update"""
        status_message = {
            "type": "status_update",
            "data": status_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(status_message)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
