# bbi_api/serializers.py
from rest_framework import serializers
from .models import Alert, Geofence, TelematicsData
from bbi_app.models import DriverProfile

class TelematicsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelematicsData
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'

class GeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = '__all__'

class DriverLocationSerializer(serializers.ModelSerializer):
    last_location = serializers.SerializerMethodField()
    
    class Meta:
        model = DriverProfile
        fields = ['id', 'user', 'device_id', 'last_location']
    
    def get_last_location(self, obj):
        last_data = TelematicsData.objects.filter(driver=obj).last()
        if last_data:
            return {
                'lat': float(last_data.latitude),
                'lng': float(last_data.longitude),
                'timestamp': last_data.timestamp
            }
        return None

class DriverDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = ['device_id', 'is_device_linked']