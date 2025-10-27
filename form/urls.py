from django.urls import path
from .views import FormListView, FormDetailView, FormDeleteView, FormUpdateView, CategoryListView
import views


urlpatterns = [
    path('forms/', FormListView.as_view(), name='form-list'),
    path('forms/<int:form_id>/detail/', FormDetailView.as_view(), name='form-detail'), 
    path('forms/<int:form_id>/update/', FormUpdateView.as_view(), name='form-update'),
    path('forms/<int:form_id>/delete/', FormDeleteView.as_view(), name='form-delete'),

    path('categories/', CategoryListView.as_view(), name='category-list'),

]
