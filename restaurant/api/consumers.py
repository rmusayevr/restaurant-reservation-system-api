from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class ReservationConsumer(WebsocketConsumer):
    def connect(self):
        self.restaurant_id = self.scope['url_route']['kwargs']['pk']
        self.room_group_name = 'admin_panel_%s' % self.restaurant_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def send_reservation_notification(self, event):
        # Send reservation notification to admin panel
        reservation_id = event['reservation_id']
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'reservation_id': reservation_id,
            'message': message
        }))
