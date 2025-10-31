from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import FormReportSerializer, ReportSubscriptionSerializer
from .models import FormReport, ReportSubscription, Form
from django.core.mail import send_mail
from form.models import Category, Form, Process, Answer

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
            return Response({"detail": "Email not found in session"}, status=400)

        try:
            form = Form.objects.get(id=form_id)
            report = FormReport.objects.get(form=form)
        except Form.DoesNotExist:
            return Response({"detail": "Form not found"}, status=404)
        except FormReport.DoesNotExist:
            return Response({"detail": "Report not found"}, status=404)

        summary_text = ""
        for q_id, data in report.summary.items():
            summary_text += f"Question: {q_id}\n"
            summary_text += f"Type: {data['type']}\n"
            summary_text += f"Answer count: {data['count']}\n"
            if data['type'] == 'rating':
                summary_text += f"Average: {data['average']}\n"
            elif data['type'] in ['select', 'checkbox']:
                summary_text += "Options:\n"
                for option, count in data['options'].items():
                    summary_text += f"  {option}: {count}\n"
            summary_text += "\n"

        send_mail(
            subject=f"Form Report: {form.title}",
            message=f"Hello!\n\nReport for form {form.title}:\n\n{summary_text}",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"detail": f"Report sent to {email}"})

class AllAnswersReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories_data = []

        categories = Category.objects.all()
        for cat in categories:
            cat_dict = {
                "id": cat.id,
                "name": cat.name,
                "forms": []
            }

            forms = cat.forms.all()
            for form in forms:
                form_dict = {
                    "id": form.id,
                    "title": form.title,
                    "processes": []
                }

                processes = form.processes.all()
                for process in processes:
                    process_dict = {
                        "id": process.id,
                        "answers": []
                    }

                    answers = process.answers.all()
                    for ans in answers:
                        answer_data = {
                            "type": ans.type,
                            "answer": ans.answer
                        }
                        process_dict["answers"].append(answer_data)

                    form_dict["processes"].append(process_dict)
                cat_dict["forms"].append(form_dict)

            categories_data.append(cat_dict)

        return Response({"categories": categories_data})