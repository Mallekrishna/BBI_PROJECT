# Update the imports in bbi_api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from django.db.models import Avg, Count, Subquery, OuterRef
from django.utils import timezone
from datetime import timedelta
from django.apps import apps
# At the top of bbi_api/views.py
from rest_framework.viewsets import ModelViewSet  # Add this import

from bbi_app.models import DriverProfile
from .models import Alert, Geofence, TelematicsData, GeofenceLog
from .serializers import (
    TelematicsDataSerializer,
    AlertSerializer,
    GeofenceSerializer,
    DriverLocationSerializer,
    DriverDeviceSerializer
)

# Add to bbi_api/views.py
class GeofenceViewSet(ModelViewSet):
    """
    API endpoint that allows geofences to be viewed or edited
    """
    queryset = Geofence.objects.all()
    serializer_class = GeofenceSerializer

# Dynamically import models to prevent circular imports
TelematicsData = apps.get_model('bbi_api', 'TelematicsData')
DriverProfile = apps.get_model('bbi_app', 'DriverProfile')
Alert = apps.get_model('bbi_api', 'Alert')
GeofenceLog = apps.get_model('bbi_api', 'GeofenceLog')

from .serializers import (
    TelematicsDataSerializer, 
    DriverDeviceSerializer, 
    DriverLocationSerializer
)

class LiveTelematicsView(APIView):
    """Endpoint for real-time telematics data"""
    def get(self, request, device_id):
        try:
            driver = DriverProfile.objects.get(device_id=device_id)
            data = TelematicsData.objects.filter(driver=driver).order_by('-timestamp')[:50]
            serializer = TelematicsDataSerializer(data, many=True)
            return Response(serializer.data)
        except DriverProfile.DoesNotExist:
            return Response(
                {"error": "Driver device not registered"},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, device_id):
        try:
            driver = DriverProfile.objects.get(device_id=device_id)
            serializer = TelematicsDataSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(driver=driver)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DriverProfile.DoesNotExist:
            return Response(
                {"error": "Invalid device ID"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# bbi_api/views.py
class DeviceRegistrationView(APIView):
    def patch(self, request, pk):
        try:
            driver = DriverProfile.objects.get(pk=pk)
            # Update directly without serializer
            device_id = request.data.get('device_id')
            if device_id:
                driver.device_id = device_id
                driver.is_device_linked = True
                driver.save()
                return Response({
                    'status': 'device linked',
                    'device_id': driver.device_id
                })
            return Response(
                {"error": "device_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DriverProfile.DoesNotExist:
            return Response(
                {"error": "Driver not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
class FleetAnalyticsView(APIView):
    """Fleet analytics for real-time tracking"""
    def get(self, request):
        active_drivers = DriverProfile.objects.filter(
            is_device_linked=True
        ).count()
        
        active_alerts = Alert.objects.filter(
            is_read=False,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        geo_violations = GeofenceLog.objects.filter(
            event_type='violation',
            timestamp__gte=timezone.now() - timedelta(days=1)
        ).count()
        
        avg_safety_score = DriverProfile.objects.aggregate(
            avg_score=Avg('safety_score')
        )['avg_score'] or 0
        
        return Response({
            'active_drivers': active_drivers,
            'active_alerts': active_alerts,
            'geo_violations': geo_violations,
            'avg_safety_score': round(avg_safety_score, 1),
            'timestamp': timezone.now()
        })

class DriverLocationView(APIView):
    """Get last known location of drivers"""
    def get(self, request):
        drivers = DriverProfile.objects.filter(
            is_device_linked=True
        ).annotate(
            last_latitude=Subquery(
                TelematicsData.objects.filter(
                    driver=OuterRef('pk')
                ).order_by('-timestamp').values('latitude')[:1]
            ),
            last_longitude=Subquery(
                TelematicsData.objects.filter(
                    driver=OuterRef('pk')
                ).order_by('-timestamp').values('longitude')[:1]
            )
        )
        
        serializer = DriverLocationSerializer(drivers, many=True)
        return Response(serializer.data)

# Add these new views to bbi_api/views.py
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView

class AlertListCreateView(ListCreateAPIView):
    """
    API endpoint that allows alerts to be viewed or created
    """
    queryset = Alert.objects.all().order_by('-timestamp')
    serializer_class = AlertSerializer
    filterset_fields = ['driver', 'is_read', 'severity']

class AlertMarkReadView(RetrieveUpdateAPIView):
    """
    API endpoint to mark alerts as read
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    
    def patch(self, request, *args, **kwargs):
        alert = self.get_object()
        alert.is_read = True
        alert.save()
        return Response({'status': 'alert marked as read'})