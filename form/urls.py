from django.urls import path
from . import views

urlpatterns = [
    path('forms/', views.form_list_create, name='form-list-create'),
    path('forms/<int:form_id>/detail/', views.form_detail, name='form-detail'),
    path('forms/<int:form_id>/update/', views.form_update, name='form-update'),
    path('forms/<int:form_id>/delete/', views.form_delete, name='form-delete'),
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
]
from . import views