from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum, Count
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .serializers import FormReportSerializer
from .models import ReportSubscription, Conclusion
from form.models import Form, Process
from rest_framework.permissions import IsAdminUser


class AllReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        aggregation = Conclusion.objects.aggregate(
            total_answers=Sum('answer_count'),
            total_reports=Count('id')
        )

        conclusions = Conclusion.objects.all().values(
            'id', 'user_id', 'process_id', 'answer_list', 'mean_rating', 'answer_count'
        )

        return Response({
            "summary": aggregation,
            "data": list(conclusions)
        })


class FormReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, process_id):
        reports = Conclusion.objects.filter(process_id=process_id)

        if not reports.exists():
            return Response({"detail": "No reports found"}, status=404)

        serializer = FormReportSerializer(reports, many=True)
        return Response(serializer.data)


class SendAllReportsEmailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        email = request.data.get("email") or request.session.get("email")
        if not email:
            return Response({"detail": "Email is required or not found in session."}, status=400)

        aggregation = Conclusion.objects.aggregate(
            total_answers=Sum('answer_count'),
            total_reports=Count('id')
        )

        conclusions = Conclusion.objects.all().values(
            'id', 'user_id', 'process_id', 'answer_list', 'mean_rating', 'answer_count'
        )

        email_text = " Summary of All Reports:\n\n"
        email_text += f"Total Answers: {aggregation['total_answers']}\n"
        email_text += f"Total Reports: {aggregation['total_reports']}\n\n"

        email_text += "Detailed Reports:\n"
        for c in conclusions:
            email_text += (
                f"- Report #{c['id']} (User {c['user_id']}, Process {c['process_id']})\n"
                f"  Mean Rating: {c['mean_rating']}\n"
                f"  Answer Count: {c['answer_count']}\n"
                f"  Answers: {c['answer_list']}\n\n"
            )

        send_mail(
            subject="All Form Reports Summary",
            message=email_text,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"detail": f"All reports sent to {email}"}, status=200)


class SendScheduledReportsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        email = request.data.get("email")
        interval = request.data.get("interval")

        if not email:
            return Response({"detail": "Email is required."}, status=400)
        if interval not in ['weekly', 'monthly']:
            return Response({"detail": "Interval must be 'weekly' or 'monthly'."}, status=400)

        now = timezone.now()
        if interval == 'weekly':
            start_time = now - timedelta(weeks=1)
        else:
            start_time = now - timedelta(days=30)

        conclusions = Conclusion.objects.filter(updated_at__gte=start_time)

        if not conclusions.exists():
            return Response({"detail": "No reports available for this interval."}, status=404)

        total_answers = sum(c.answer_count for c in conclusions)
        mean_rating = (
            sum(c.mean_rating or 0 for c in conclusions) / len(conclusions)
            if conclusions else 0)

        email_text = f" {interval.capitalize()} Report Summary\n\n"
        email_text += f"Total Answers: {total_answers}\nAverage Rating: {mean_rating:.2f}\n\n"

        for c in conclusions:
            email_text += (
                f"- Report #{c.id} (User {c.user_id}, Process {c.process_id})\n"
                f"  Mean Rating: {c.mean_rating}\n"
                f"  Answer Count: {c.answer_count}\n"
                f"  Answers: {c.answer_list}\n\n")

        send_mail(
            subject=f"{interval.capitalize()} Report",
            message=email_text,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,)

        return Response(
            {"detail": f"{interval.capitalize()} report sent to {email} successfully."},
            status=200)
