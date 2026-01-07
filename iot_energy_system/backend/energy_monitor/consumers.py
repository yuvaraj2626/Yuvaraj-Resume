"""
WebSocket consumers for real-time data streaming.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class SensorDataConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time sensor data."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.room_group_name = 'sensor_data'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        pass
    
    async def sensor_reading(self, event):
        """Receive sensor reading from room group."""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'sensor_reading',
            'data': event['data']
        }))


class AlertConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time alerts."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.room_group_name = 'alerts'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        pass
    
    async def alert_notification(self, event):
        """Receive alert notification from room group."""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'data': event['data']
        }))
