from django.urls import path
from .views import FormReportView, SubscribeReportView, SendFormReportEmailAPIView

urlpatterns = [
    path('report/form/<int:form_id>/', FormReportView.as_view(), name='form-report'),
    path('report/subscribe/<int:form_id>/', SubscribeReportView.as_view(), name='subscribe-report'),
    path('report/send-email/<int:form_id>/', SendFormReportEmailAPIView.as_view(), name='send-report-email'),
]

