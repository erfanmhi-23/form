from django.urls import path
from .views import FormListView, FormDetailView, FormDeleteView, FormUpdateView,AnswerView
import views


urlpatterns = [
    path('forms/', FormListView.as_view(), name='form-list'),
    path('forms/<int:form_id>/detail/', FormDetailView.as_view(), name='form-detail'), 
    path('forms/<int:form_id>/update/', FormUpdateView.as_view(), name='form-update'),
    path('forms/<int:form_id>/delete/', FormDeleteView.as_view(), name='form-delete'),

    path('forms/<int:form_id>/text/', views.text_list_create, name='text-list-create'),
    path('forms/<int:form_id>/text/<int:text_id>/detail/', views.text_detail, name='text-detail'),
    path('forms/<int:form_id>/text/<int:text_id>/update/', views.text_update, name='text-update'),
    path('forms/<int:form_id>/text/<int:text_id>/delete/', views.text_delete, name='text-delete'),

    path('forms/<int:form_id>/select/', views.select_list_create, name='select-list-create'),
    path('forms/<int:form_id>/select/<int:select_id>/detail/', views.select_detail, name='select-detail'),
    path('forms/<int:form_id>/select/<int:select_id>/update/', views.select_update, name='select-update'),
    path('forms/<int:form_id>/select/<int:select_id>/delete/', views.select_delete, name='select-delete'),

    path('forms/<int:form_id>/rating/', views.rating_list_create, name='rating-list-create'),
    path('forms/<int:form_id>/rating/<int:rating_id>/detail/', views.rating_detail, name='rating-detail'),
    path('forms/<int:form_id>/rating/<int:rating_id>/update/', views.rating_update, name='rating-update'),
    path('forms/<int:form_id>/rating/<int:rating_id>/delete/', views.rating_delete, name='rating-delete'),

    path('forms/<int:form_id>/answers/', AnswerView.as_view(), name='submit-answers'),
]
