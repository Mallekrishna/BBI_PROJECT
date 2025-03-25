"""# bbi_api/urls.py
from django.urls import path, include
from .views import LiveTelematicsView, FleetAnalyticsView, DriverLocationView, AlertListCreateView, MarkAlertReadView, GeofenceViewSet

urlpatterns = [
     path('telematics-api/<str:device_id>/', LiveTelematicsView.as_view(), name='telematics_api'),
    #path('telematics/<str:device_id>/', LiveTelematicsView.as_view()),
]

urlpatterns += [
    path('fleet/analytics/', FleetAnalyticsView.as_view()),
    path('fleet/locations/', DriverLocationView.as_view()),
    path('alerts/', include([
        path('', AlertListCreateView.as_view()),
        path('<int:pk>/mark-read/', MarkAlertReadView.as_view()),
    ])),
    path('geofences/', GeofenceViewSet.as_view({'get': 'list', 'post': 'create'})),
]"""



# bbi_api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LiveTelematicsView,
    FleetAnalyticsView,
    DriverLocationView,
    AlertListCreateView,
    AlertMarkReadView,
    GeofenceViewSet,
    DeviceRegistrationView
)

router = DefaultRouter()
router.register(r'geofences', GeofenceViewSet)

urlpatterns = [
    path('telematics/<str:device_id>/', LiveTelematicsView.as_view()),
    path('fleet/analytics/', FleetAnalyticsView.as_view()),
    path('fleet/locations/', DriverLocationView.as_view()),
    path('alerts/', include([
        path('', AlertListCreateView.as_view(), name='alert-list'),
        path('<int:pk>/mark-read/', AlertMarkReadView.as_view(), name='alert-mark-read'),
    ])),
    path('drivers/<int:pk>/link-device/', DeviceRegistrationView.as_view()),
    path('', include(router.urls)),
]