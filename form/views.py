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

    def post(self, request):
        serializer = FormSerializer(data=request.data)
        if serializer.is_valid():
            created = serializer.save()
            return Response(FormSerializer(created).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FormDetailView(APIView):
    def get(self, request, form_id):
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FormSerializer(form)
        return Response(serializer.data)
