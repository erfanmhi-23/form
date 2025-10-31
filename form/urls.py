from django.urls import path
from .views import FormListView, FormDetailView, FormDeleteView, FormUpdateView, CategoryListView, CategoryRenameView, AnswerView, ProcessListCreateAPIView, ProcessRetrieveAPIView,NextFormView



urlpatterns = [
    path('forms/', FormListView.as_view(), name='form-list'),
    path('forms/<int:form_id>/detail/', FormDetailView.as_view(), name='form-detail'), 
    path('forms/<int:form_id>/update/', FormUpdateView.as_view(), name='form-update'),
    path('forms/<int:form_id>/delete/', FormDeleteView.as_view(), name='form-delete'),

    #category
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:category_id>/rename/', CategoryRenameView.as_view(), name='category-rename'),

    path('processes/', ProcessListCreateAPIView.as_view(), name='process-list-create'),
    path('processes/<int:pk>/', ProcessRetrieveAPIView.as_view(), name='process-detail'),

    path('forms/answers/', AnswerView.as_view(), name='submit-answers'),

    path('processes/<int:process_id>/answers/', AnswerView.as_view(), name='submit-answers'),
    path('processes/<int:process_id>/next/', NextFormView.as_view(), name='process-next-form'),
]
