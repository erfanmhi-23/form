from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Form
from .serializers import FormSerializer

class FormListView(APIView):
    def get(self, request):
        forms = Form.objects.all()
        serializer = FormSerializer(forms, many=True)
        return Response(serializer.data)

class FormDetailView(APIView):
    def get(self, request, form_id):
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FormSerializer(form)
        return Response(serializer.data)