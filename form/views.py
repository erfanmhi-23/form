from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions , generics
from .serializers import FormSerializer, CategorySerializer,AnswerSerializer, ProcessSerializer
from .models import Form,Process,Answer, Category


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


#category
class CategoryListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            created_cat = serializer.save()
            return Response(CategorySerializer(created_cat).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryRenameView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, category_id):
        try:
            c = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        name = request.data.get('name')
        if not name:
            return Response({'name': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        c.name = name
        c.save(update_fields=['name'])
        return Response({'id': c.id, 'name': c.name}, status=status.HTTP_200_OK)
    
class ProcessListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        process = serializer.save()
        return Response(ProcessSerializer(process).data, status=status.HTTP_201_CREATED)


class ProcessRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

class AnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        ثبت پاسخ‌ها برای یک Process (که خودش شامل چند فرم است).
        ورودی:
        {
            "process_id": 5,
            "answers": [
                {"form_id": 2, "type": "text", "answer": "Blue"},
                {"form_id": 3, "type": "rating", "answer": 4}
            ]
        }
        """
        process_id = request.data.get('process_id')
        answers_data = request.data.get('answers', [])

        if not process_id:
            return Response({'error': 'process_id is required.'}, status=400)

        try:
            process = Process.objects.prefetch_related('forms').get(id=process_id)
        except Process.DoesNotExist:
            return Response({'error': 'Process not found.'}, status=404)
        
        if not answers_data:
            return Response({'error': 'answers cannot be empty.'}, status=400)

        process_forms = {f.id: f for f in process.forms.all()}  # dict برای دسترسی سریع
        created_answers = []

        for item in answers_data:
            form_id = item.get('form_id')
            answer_type = item.get('type')
            answer_value = item.get('answer')

            # بررسی وجود فرم در پروسس
            form = process_forms.get(form_id)
            if not form:
                return Response({
                    'error': f'Form {form_id} does not belong to this process.'
                }, status=400)

            # بررسی نوع پاسخ با نوع فرم
            if answer_type != form.type:
                return Response({
                    'error': f'Type mismatch: Form type is {form.type}, but answer type is {answer_type}.',
                    'form_id': form.id
                }, status=400)

            # اعتبارسنجی پاسخ‌ها مثل قبل
            if answer_type in ['select', 'checkbox']:
                if isinstance(answer_value, list):
                    invalid_options = [opt for opt in answer_value if opt not in form.options]
                    if invalid_options:
                        return Response({
                            'error': 'Invalid option(s) selected.',
                            'invalid_options': invalid_options,
                            'form_id': form.id
                        }, status=400)
                else:
                    if answer_value not in form.options:
                        return Response({
                            'error': 'Invalid option selected.',
                            'invalid_option': answer_value,
                            'form_id': form.id
                        }, status=400)

            elif answer_type == 'rating':
                try:
                    rating_value = int(answer_value)
                except (ValueError, TypeError):
                    return Response({
                        'error': 'Rating must be an integer.',
                        'form_id': form.id
                    }, status=400)

                # چک اینکه rating داخل گزینه‌های فرم باشد
                allowed_options = [int(opt) for opt in form.options]  # تبدیل options به int
                if rating_value not in allowed_options:
                    return Response({
                        'error': f'Invalid rating. Must be one of {allowed_options}.',
                        'form_id': form.id,
                        'invalid_rating': rating_value
                    }, status=400)

            # ذخیره پاسخ
            serializer = AnswerSerializer(data={
                'form': form.id,
                'process': process.id,
                'type': answer_type,
                'answer': answer_value
            })

            if serializer.is_valid():
                serializer.save()
                created_answers.append(serializer.data)
            else:
                return Response(serializer.errors, status=400)

        return Response({
            'message': 'Answers saved successfully.',
            'process_id': process.id,
            'answers': created_answers
        }, status=201)
