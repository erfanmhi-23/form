from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions,status
from .serializers import FormReportSerializer
from .models import ReportSubscription, Form,FormReport
from django.core.mail import send_mail



class FormReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, form_id):
        user = request.user
        if not user.is_staff:
            return Response({"detail": "Not authorized"}, status=403)

        try:
            report = FormReport.objects.get(form_id=form_id)
        except FormReport.DoesNotExist:
            return Response({"detail": "Report not found"}, status=404)

        serializer = FormReportSerializer(report)
        return Response(serializer.data)


class SubscribeReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, form_id):
        email = request.data.get('email')
        interval = request.data.get('interval', 'weekly')
        
        if not email:
            return Response({"error": "Email is required"}, status=400)
        
        if interval not in ['weekly', 'monthly']:
            return Response({"error": "Invalid interval"}, status=400)
        
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({"error": "Form not found"}, status=404)
        
        sub, created = ReportSubscription.objects.get_or_create(
            form=form,
            email=email,
            defaults={"interval": interval}
        )
        if not created:
            sub.interval = interval
            sub.save()

        return Response({"message": f"Subscription saved for {email}", "interval": interval})


class SendFormReportEmailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, form_id):
        email = request.session.get('email')
        if not email:
            return Response({"detail": "ایمیل در session وجود ندارد."}, status=400)

        try:
            form = Form.objects.get(id=form_id)
            report = FormReport.objects.get(form=form)
        except Form.DoesNotExist:
            return Response({"detail": "فرم پیدا نشد."}, status=404)
        except FormReport.DoesNotExist:
            return Response({"detail": "گزارش برای این فرم موجود نیست."}, status=404)

        summary_text = ""
        for q_id, data in report.summary.items():
            summary_text += f"سوال: {q_id}\n"
            summary_text += f"نوع: {data['type']}\n"
            summary_text += f"تعداد پاسخ‌ها: {data['count']}\n"
            if data['type'] == 'rating':
                summary_text += f"میانگین: {data['average']}\n"
            elif data['type'] == 'select':
                summary_text += "گزینه‌ها:\n"
                for option, count in data['options'].items():
                    summary_text += f"  {option}: {count}\n"
            summary_text += "\n"

        send_mail(
            subject=f"گزارش فرم: {form.title}",
            message=f"سلام!\n\nگزارش فرم {form.title} به شرح زیر است:\n\n{summary_text}",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"detail": f"گزارش برای {email} ارسال شد."})
