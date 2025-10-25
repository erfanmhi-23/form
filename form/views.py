from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Form,Process,Answer
from .serializers import FormSerializer,AnswerSerializer, ProcessSerializer

class FormListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
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
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, form_id):
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FormSerializer(form)
        return Response(serializer.data)
    
class FormDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, form_id):
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

        form.delete()
        return Response({'message': 'Form deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
class FormUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def put(self, request, form_id):
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FormSerializer(form, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, form_id):
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FormSerializer(form, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, form_id):

    # Record answers submitted for a specific form.
    # Expected payload:
    # {
    #     "answers": [
    #         {"type": "text", "answer": "Blue"},
    #         {"type": "number", "answer": 42}
    #     ]
    # }

        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

        process = Process.objects.create(
            form=form,
            liner=False,
            password=None,
            view_count=0
        )

        answers_data = request.data.get('answers', [])
        created_answers = []

        for item in answers_data:
            serializer = AnswerSerializer(data={
                'form': form.id,
                'process': process.id,
                'type': item.get('type'),
                'answer': item.get('answer')
            })

            if serializer.is_valid():
                serializer.save()
                created_answers.append(serializer.data)
            else:
                process.delete()  # rollback
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'Answers saved successfully.',
            'process_id': process.id,
            'answers': created_answers
        }, status=status.HTTP_201_CREATED)
