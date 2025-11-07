from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Answer, Conclusion
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import re

@receiver(post_save, sender=Answer)
def update_form_report(sender, instance, created, **kwargs):
    if created:
        process = instance.process
        report, _ = Conclusion.objects.get_or_create(process=process)

        report.answer_count = process.answers.count()
        report.view_count = process.view_count

        summary = {}
        for ans in process.answers.all():
            q_id = f"question_{ans.id}"
            if q_id not in summary:
                summary[q_id] = {"type": ans.type, "count": 0}
                if ans.type == "rating":
                    summary[q_id]["total"] = 0
                elif ans.type in ["select", "checkbox"]:
                    summary[q_id]["options"] = {}

            summary[q_id]["count"] += 1
            if ans.type == "rating":
                summary[q_id]["total"] += int(ans.answer)
            elif ans.type == "select":
                summary[q_id]["options"][ans.answer] = summary[q_id]["options"].get(ans.answer, 0) + 1
            elif ans.type == "checkbox":
                for opt in ans.answer:
                    summary[q_id]["options"][opt] = summary[q_id]["options"].get(opt, 0) + 1

        for q_id, data in summary.items():
            if data["type"] == "rating" and data["count"] > 0:
                data["average"] = data["total"] / data["count"]
                data.pop("total")

        report.summary = summary
        report.save()

        safe_id = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", str(process.id))
        group_name = f"form_report_{safe_id}"

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "send_report", "report": report.summary or {}}
        )
