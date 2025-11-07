from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum, Count
from django.core.mail import send_mail
from .serializers import FormReportSerializer
from .models import ReportSubscription, Conclusion #here <------------------------
from form.models import Category, Form, Process, Answer #here <------------------------

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


class SendFormReportEmailAPIView(APIView): #here <------------------------
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, form_id):
        email = request.session.get('email')
        if not email:
            return Response({"detail": "Email not found in session"}, status=400)

        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({"detail": "فرم پیدا نشد."}, status=404)

        # گزارش را از طریق process مربوط به همان فرم پیدا می‌کنیم
        report = Conclusion.objects.filter(process__form=form).order_by('-updated_at').first()
        if not report:
            return Response({"detail": "گزارش برای این فرم موجود نیست."}, status=404)

        # ساخت متن ایمیل بر اساس فیلدهای موجود در Conclusion
        summary_text = []
        summary_text.append(f"Total answers: {report.answer_count}")
        if report.mean_rating is not None:
            summary_text.append(f"Mean rating: {report.mean_rating}")

        # اگر answer_list ساختار سوال/گزینه دارد، آن را هم اضافه کن
        if isinstance(report.answer_list, dict):
            summary_text.append("Answers:")
            for q_key, val in report.answer_list.items():
                summary_text.append(f"- {q_key}: {val}")

        body = "Hello!\n\nReport for form {title}:\n\n{content}".format(
            title=form.title,
            content="\n".join(summary_text)
        )

        send_mail(
            subject=f"Form Report: {form.title}",
            message=body,
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({"detail": f"Report sent to {email}"})
#------------------------

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
