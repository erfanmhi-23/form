from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/report/(?P<process_id>\d+)/$', consumers.FormReportConsumer.as_asgi()),
]