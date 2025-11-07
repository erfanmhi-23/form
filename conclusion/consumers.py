import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class FormReportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # اگر نمیخوای دسترسی محدود باشه، خط زیر رو میتونی کامنت کنی
        user = self.scope['user']

        self.process_id = self.scope['url_route']['kwargs']['process_id']
        # امن‌سازی نام گروه
        safe_id = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", str(self.process_id))
        self.group_name = f"form_report_{safe_id}"

        # اضافه شدن به گروه
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # ارسال summary فعلی به محض کانکت
        await self.send_current_summary()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name") and self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_report(self, event):
        await self.send(text_data=json.dumps(event['report']))

    async def send_current_summary(self):
        from form.models import Process, Conclusion
        try:
            process = await sync_to_async(Process.objects.get)(id=self.process_id)
            report, _ = await sync_to_async(Conclusion.objects.get_or_create)(process=process)
            await self.send(text_data=json.dumps(report.summary or {}))
        except Exception:
            await self.send(text_data=json.dumps({}))
