from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions , generics
from django.db import models
from .serializers import FormSerializer, CategorySerializer,AnswerSerializer, ProcessSerializer
from .models import Form,Process, Category 
from conclusion.models import Conclusion


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
        process_id = request.data.get('process_id')
        process_password = request.data.get('process_password')
        answers_data = request.data.get('answers', [])

        if not process_id:
            return Response({'error': 'process_id is required.'}, status=400)

        try:
            process = Process.objects.prefetch_related('forms').get(id=process_id)
        except Process.DoesNotExist:
            return Response({'error': 'Process not found.'}, status=404)

        # 🔐 بررسی پسورد پروسس
        if process.password:
            if not process_password:
                return Response({'error': 'Process password is required.'}, status=400)
            if process_password != process.password:
                return Response({'error': 'Invalid process password.'}, status=403)

        if not answers_data:
            return Response({'error': 'answers cannot be empty.'}, status=400)

        process_forms_qs = process.forms.all()
        process_forms = {f.id: f for f in process_forms_qs}
        created_answers = []

        # 🟢 فرم‌های فعال و اجباری
        active_forms = [f for f in process_forms_qs if f.validation]
        required_forms = [f for f in active_forms if f.force]

        answered_form_ids = [a.get('form_id') for a in answers_data]
        missing_required_forms = [
            f.id for f in required_forms if f.id not in answered_form_ids
        ]
        if missing_required_forms:
            missing_titles = [process_forms[fid].title for fid in missing_required_forms]
            return Response({
                'error': 'Some required forms were not answered.',
                'missing_forms': missing_required_forms,
                'missing_titles': missing_titles
            }, status=400)

        # ✅ شماره‌گذاری سوال‌ها
        question_numbers = {}
        counter = 1
        for form in process_forms_qs:
            if form.question_num:
                question_numbers[form.id] = counter
                counter += 1

        # 🟡 حلقه‌ی ذخیره پاسخ‌ها
        for item in answers_data:
            form_id = item.get('form_id')
            answer_type = item.get('type')
            answer_value = item.get('answer')
            provided_password = item.get('password')

            form = process_forms.get(form_id)
            if not form:
                return Response({
                    'error': f'Form {form_id} does not belong to this process.'
                }, status=400)

            if not form.validation:
                return Response({
                    'error': f'Form \"{form.title}\" is disabled and cannot be answered.',
                    'form_id': form.id
                }, status=400)

            # 🔐 بررسی پسورد فرم
            if form.password:
                if not provided_password:
                    return Response({
                        'error': f'Password is required for form \"{form.title}\".',
                        'form_id': form.id
                    }, status=400)
                if provided_password != form.password:
                    return Response({
                        'error': f'Invalid password for form \"{form.title}\".',
                        'form_id': form.id
                    }, status=403)

            # بررسی نوع پاسخ
            if answer_type != form.type:
                return Response({
                    'error': f'Type mismatch: Form type is {form.type}, but answer type is {answer_type}.',
                    'form_id': form.id
                }, status=400)

            # 🧩 اعتبارسنجی بر اساس نوع
            if answer_type in ['select', 'checkbox']:
                if isinstance(answer_value, list):
                    invalid_options = [opt for opt in answer_value if opt not in form.options]
                    if invalid_options:
                        return Response({
                            'error': 'Invalid option(s) selected.',
                            'invalid_options': invalid_options,
                            'form_id': form.id,
                            'allowed_options': form.options  
                        }, status=400)
                else:
                    if answer_value not in form.options:
                        return Response({
                            'error': 'Invalid option selected.',
                            'invalid_option': answer_value,
                            'form_id': form.id,
                            'allowed_options': form.options  
                        }, status=400)

            elif answer_type == 'rating':
                try:
                    rating_value = int(answer_value)
                except (ValueError, TypeError):
                    return Response({
                        'error': 'Rating must be an integer.',
                        'form_id': form.id
                    }, status=400)

                allowed_options = [int(opt) for opt in form.options]
                if rating_value not in allowed_options:
                    return Response({
                        'error': f'Invalid rating. Must be one of {allowed_options}.',
                        'form_id': form.id,
                        'invalid_rating': rating_value
                    }, status=400)

            elif answer_type == 'text':
                if not isinstance(answer_value, str):
                    return Response({
                        'error': 'Answer for text form must be a string.',
                        'form_id': form.id
                    }, status=400)

                text_length = len(answer_value.strip())
                if text_length < form.min:
                    return Response({
                        'error': f'Text answer is too short. Minimum length is {form.min} characters.',
                        'form_id': form.id,
                        'length': text_length
                    }, status=400)

                if text_length > form.max:
                    return Response({
                        'error': f'Text answer is too long. Maximum length is {form.max} characters.',
                        'form_id': form.id,
                        'length': text_length
                    }, status=400)

            # ✅ ذخیره پاسخ
            serializer = AnswerSerializer(data={
                'form': form.id,
                'process': process.id,
                'type': answer_type,
                'answer': answer_value
            })

            if serializer.is_valid():
                saved_answer = serializer.save()
                serialized_data = serializer.data

                if form.id in question_numbers:
                    serialized_data['question_number'] = question_numbers[form.id]

                created_answers.append(serialized_data)

                # ✅ افزایش view_count فرم
                form.view_count = models.F('view_count') + 1
                form.save(update_fields=['view_count'])
            else:
                return Response(serializer.errors, status=400)

        # ✅ افزایش view_count پروسس
        process.view_count = models.F('view_count') + 1
        process.save(update_fields=['view_count'])
        # 🧭 اگر liner فعاله، فرم بعدی رو بده
        next_form_data = None
        if process.liner:
            all_forms = process.forms.order_by('id')
            answered_form_ids = Answer.objects.filter(process=process).values_list('form_id', flat=True)

            next_form = next((f for f in all_forms if f.id not in answered_form_ids), None)
            if next_form:
                next_form_data = FormSerializer(next_form).data
            else:
                next_form_data = 'All questions answered.'

        # پاسخ نهایی
        response_data = {
            'message': 'Answers saved successfully.',
            'process_id': process.id,
            'answers': created_answers,
        }

        if next_form_data is not None:
            response_data['next_form'] = next_form_data

        return Response(response_data, status=201)

class NextFormView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, process_id):
        try:
            process = Process.objects.prefetch_related('forms').get(id=process_id)
        except Process.DoesNotExist:
            return Response({'error': 'Process not found'}, status=404)

        if not process.liner:
            forms = process.forms.all()
            serializer = FormSerializer(forms, many=True)
            return Response({'forms': serializer.data}, status=200)

        all_forms = process.forms.order_by('id')
        answered_form_ids = Answer.objects.filter(process=process).values_list('form_id', flat=True)

        next_form = None
        for form in all_forms:
            if form.id not in answered_form_ids:
                next_form = form
                break

        if not next_form:
            return Response({'message': 'All questions answered.'}, status=200)

        serializer = FormSerializer(next_form)
        return Response({'next_form': serializer.data}, status=200)
