from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Answer, Conclusion
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Answer)
def update_form_report(sender, instance, created, **kwargs):
    if created:
        form = instance.form
        report, _ = Conclusion.objects.get_or_create(form=form)

        report.answer_count = form.answers.count()
        report.view_count = form.view_count

        summary = {}
        answers = form.answers.all()
        for ans in answers:
            q_id = f"question_{ans.id}"
            if q_id not in summary:
                summary[q_id] = {"type": ans.type, "count": 0}
                if ans.type == "rating":
                    summary[q_id]["total"] = 0
                elif ans.type == "select":
                    summary[q_id]["options"] = {}

            summary[q_id]["count"] += 1

            if ans.type == "rating":
                summary[q_id]["total"] += int(ans.answer)
            elif ans.type == "select":
                summary[q_id]["options"][ans.answer] = summary[q_id]["options"].get(ans.answer, 0) + 1

        for q_id, data in summary.items():
            if data["type"] == "rating" and data["count"] > 0:
                data["average"] = data["total"] / data["count"]
                data.pop("total")

        report.summary = summary
        report.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"form_report_{form.id}",
            {"type": "send_report", "report": report.summary}
        )
