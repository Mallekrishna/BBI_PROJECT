# bbi_api/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/telematics/(?P<device_id>[^/]+)/$', consumers.TelematicsConsumer.as_asgi()),
]