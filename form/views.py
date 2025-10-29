from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
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
    
#چت بات 
#test
class AnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, form_id):
        """
        ثبت پاسخ‌های یک فرم مشخص.
        فرمت ورودی:
        {
            "answers": [
                {"type": "text", "answer": "Blue"},
                {"type": "select", "answer": "Option 1"},
                {"type": "checkbox", "answer": ["Option 2", "Option 3"]},
                {"type": "rating", "answer": 4}
            ]
        }
        """
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

        # ایجاد Process جدید برای این فرم
        process = Process.objects.create(
            form=form,
            liner=False,
            password=None,
            view_count=0
        )

        answers_data = request.data.get('answers', [])
        created_answers = []

        for item in answers_data:
            answer_type = item.get('type')
            answer_value = item.get('answer')

            # --- منطق select / checkbox ---
            if answer_type in ['select', 'checkbox']:
                if isinstance(answer_value, list):
                    # checkbox چند گزینه‌ای
                    invalid_options = [opt for opt in answer_value if opt not in form.options]
                    if invalid_options:
                        process.delete()  # rollback
                        return Response({
                            'error': 'Invalid option(s) selected.',
                            'invalid_options': invalid_options
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # select تک گزینه
                    if answer_value not in form.options:
                        process.delete()  # rollback
                        return Response({
                            'error': 'Invalid option selected.',
                            'invalid_option': answer_value
                        }, status=status.HTTP_400_BAD_REQUEST)

            # --- منطق rating ---
            elif answer_type == 'rating':
                try:
                    rating_value = int(answer_value)
                except (ValueError, TypeError):
                    process.delete()
                    return Response({
                        'error': 'Rating must be an integer.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                if rating_value < 1 or rating_value > form.max:
                    process.delete()
                    return Response({
                        'error': f'Rating must be between 1 and {form.max}.',
                        'invalid_rating': rating_value
                    }, status=status.HTTP_400_BAD_REQUEST)

            # --- ذخیره پاسخ ---
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
                process.delete()  # rollback
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'Answers saved successfully.',
            'process_id': process.id,
            'answers': created_answers
        }, status=status.HTTP_201_CREATED)
