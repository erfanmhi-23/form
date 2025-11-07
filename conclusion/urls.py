from django.urls import path
from .views import FormReportView,SendAllReportsEmailAPIView ,AllReportView

urlpatterns = [
    path('report/form/<int:process_id>/', FormReportView.as_view(), name='form-report'),
    path('Allreport/', AllReportView.as_view(), name='all_report'),
    path('report/send-all/', SendAllReportsEmailAPIView.as_view(), name='send-all-reports'),

]
