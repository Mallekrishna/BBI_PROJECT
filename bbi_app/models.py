from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models  # ✅ Correct


class DriverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    policy_number = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15)
    join_date = models.DateField(auto_now_add=True)
    is_device_linked = models.BooleanField(default=False)
    device_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Discount fields
    participation_discount = models.FloatField(default=0.05)  # 5% initial discount
    driving_discount = models.FloatField(default=0.0)
    total_discount = models.FloatField(default=0.05)
    
    def update_discounts(self):
        """Calculate total discount based on participation and driving behavior"""
        self.total_discount = min(0.30, self.participation_discount + self.driving_discount)
        self.save()
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.policy_number}"

class DrivingTrip(models.Model):
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='trips')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    distance_miles = models.FloatField(validators=[MinValueValidator(0)])
    
    # Driving metrics
    average_speed = models.FloatField(validators=[MinValueValidator(0)])
    max_speed = models.FloatField(validators=[MinValueValidator(0)])
    hard_brakes = models.IntegerField(validators=[MinValueValidator(0)])
    rapid_accelerations = models.IntegerField(validators=[MinValueValidator(0)])
    night_driving = models.BooleanField(default=False)
    
    # Scores (0-100)
    speed_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    braking_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    acceleration_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    overall_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    def save(self, *args, **kwargs):
        """Calculate overall score before saving"""
        self.overall_score = (self.speed_score + self.braking_score + self.acceleration_score) / 3
        super().save(*args, **kwargs)
        
        # Update driver's discount based on new trip data
        self.driver.driving_discount = self.calculate_driving_discount()
        self.driver.update_discounts()
    
    def calculate_driving_discount(self):
        """Calculate driving discount based on trip history"""
        trips = DrivingTrip.objects.filter(driver=self.driver).order_by('-end_time')[:30]  # Last 30 trips
        
        if not trips:
            return 0.0
            
        avg_score = sum(t.overall_score for t in trips) / len(trips)
        
        # Convert average score to discount (0-25%)
        return min(0.25, avg_score / 100 * 0.25)
    
    def __str__(self):
        return f"Trip {self.id} - {self.driver.user.get_full_name()}"

class DiscountHistory(models.Model):
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='discount_history')
    date = models.DateField(auto_now_add=True)
    participation_discount = models.FloatField()
    driving_discount = models.FloatField()
    total_discount = models.FloatField()
    
    def __str__(self):
        return f"Discount update for {self.driver} on {self.date}"
    


def update_safety_score(self):
    """Calculate dynamic safety score based on recent trips"""
    recent_trips = self.trips.order_by('-end_time')[:30]
    if not recent_trips:
        return 0
    
    # Calculate weighted scores
    speed_scores = [t.speed_score * 0.4 for t in recent_trips]
    brake_scores = [t.braking_score * 0.3 for t in recent_trips]
    accel_scores = [t.acceleration_score * 0.3 for t in recent_trips]
    
    avg_score = (
        sum(speed_scores) / len(speed_scores) +
        sum(brake_scores) / len(brake_scores) +
        sum(accel_scores) / len(accel_scores)
    )
    
    # Apply alert penalties
    alert_penalty = min(10, self.alerts.filter(is_read=False).count() * 0.5)
    return max(0, avg_score - alert_penalty)