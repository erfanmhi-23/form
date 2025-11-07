from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from rest_framework import permissions,status
from .serializers import FormReportSerializer
from .models import ReportSubscription, Form,Conclusion
from django.core.mail import send_mail
from form.models import Category, Form, Process, Answer
from django.conf import settings
from rest_framework.permissions import IsAdminUser

class AllReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, process_id):
        user = request.user

        if not user.is_staff:
            return Response({"detail": "Not authorized"}, status=403)

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

        email_text = f"📊 Summary of All Reports:\n\n"
        email_text += f"Total Answers: {aggregation['total_answers']}\n"
        email_text += f"Total Reports: {aggregation['total_reports']}\n\n"

        email_text += "Detailed Reports:\n"
        for c in conclusions:
            email_text += f"- Report #{c['id']} (User {c['user_id']}, Process {c['process_id']})\n"
            email_text += f"  Mean Rating: {c['mean_rating']}\n"
            email_text += f"  Answer Count: {c['answer_count']}\n"
            email_text += f"  Answers: {c['answer_list']}\n\n"

        send_mail(
            subject="All Form Reports Summary",
            message=email_text,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"detail": f"All reports sent to {email}"}, status=200)