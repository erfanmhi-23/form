from channels.generic.websocket import AsyncWebsocketConsumer
import json

class FormReportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_staff:
            await self.close()
            return

        self.form_id = self.scope['url_route']['kwargs']['form_id']
        self.group_name = f"form_report_{self.form_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_report(self, event):
        await self.send(text_data=json.dumps(event['report']))
