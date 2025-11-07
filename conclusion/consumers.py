from channels.generic.websocket import AsyncWebsocketConsumer
import json

class FormReportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_staff:
            await self.close()
            return

        process_id = self.scope['url_route']['kwargs']['process_id']
        safe_id = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", str(process_id))
        self.group_name = f"form_report_{safe_id}"
        if len(self.group_name) > 100:
            self.group_name = self.group_name[:100]

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name") and self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
