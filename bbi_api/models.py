# bbi_api/models.py
from django.db import models
from bbi_app.models import DriverProfile


class TelematicsData(models.Model):
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='telematics_data')
    timestamp = models.DateTimeField(auto_now_add=True)
    speed = models.FloatField()  # Current speed in mph
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    acceleration = models.FloatField()  # Current acceleration in m/s²
    brake_force = models.FloatField(null=True, blank=True)  # Brake pressure
    is_hard_brake = models.BooleanField(default=False)
    rpm = models.IntegerField(null=True, blank=True)  # Engine RPM
    fuel_level = models.FloatField(null=True, blank=True)  # Percentage

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['driver', '-timestamp']),
        ]

    def __str__(self):
        return f"Telematics {self.id} - {self.driver} at {self.timestamp}"
    
    
class AlertRule(models.Model):
    ALERT_TYPES = [
        ('speed', 'Speed Threshold'),
        ('geo', 'Geofence Violation'),
        ('hard_brake', 'Hard Braking'),
        ('accel', 'Rapid Acceleration'),
    ]
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold = models.FloatField()
    is_active = models.BooleanField(default=True)

class Alert(models.Model):
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE)
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    severity = models.CharField(max_length=10, choices=[('low','Low'),('med','Medium'),('high','High')])
    
    

class Geofence(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius = models.FloatField()  # in meters
    is_allowed = models.BooleanField(default=True)  # True=allowed zone, False=restricted

class GeofenceLog(models.Model):
    geofence = models.ForeignKey(Geofence, on_delete=models.CASCADE)
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=10, choices=[('entry','Entry'),('exit','Exit')])