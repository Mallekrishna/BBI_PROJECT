from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from .models import DriverProfile, DrivingTrip, DiscountHistory
from django.db.models import Avg, Count

# ===== Inline Admin Classes =====
class DriverProfileInline(admin.StackedInline):
    model = DriverProfile
    can_delete = False
    verbose_name_plural = 'Driver Profiles'
    fields = ('policy_number', 'phone_number', 'is_device_linked', 'device_id', 
              'participation_discount', 'driving_discount', 'total_discount')
    readonly_fields = ('total_discount',)

class DrivingTripInline(admin.TabularInline):
    model = DrivingTrip
    extra = 0
    fields = ('start_time', 'end_time', 'distance_miles', 'overall_score', 'trip_actions')
    readonly_fields = ('trip_actions',)
    
    def trip_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">View</a>',
            reverse('admin:bbi_app_drivingtrip_change', args=[obj.id])
        )
    trip_actions.short_description = 'Actions'

class DiscountHistoryInline(admin.TabularInline):
    model = DiscountHistory
    extra = 0
    fields = ('date', 'participation_discount', 'driving_discount', 'total_discount')
    readonly_fields = fields

# ===== Main Admin Classes =====
@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user_info', 'policy_number', 'device_status', 'current_discount', 'trip_count', 'avg_score')
    list_filter = ('is_device_linked',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'policy_number')
    inlines = [DrivingTripInline, DiscountHistoryInline]
    actions = ['recalculate_discounts']
    readonly_fields = ('discount_progress',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'policy_number', 'phone_number')
        }),
        ('Device Information', {
            'fields': ('is_device_linked', 'device_id')
        }),
        ('Discount Information', {
            'fields': ('participation_discount', 'driving_discount', 'total_discount', 'discount_progress')
        }),
    )

    def user_info(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.username})"
    user_info.short_description = 'Driver'
    user_info.admin_order_field = 'user__first_name'

    def device_status(self, obj):
        return "✅ Linked" if obj.is_device_linked else "❌ Not Linked"
    device_status.short_description = 'Device'

    def current_discount(self, obj):
        return f"{obj.total_discount * 100:.1f}%"
    current_discount.short_description = 'Discount'
    current_discount.admin_order_field = 'total_discount'

    def trip_count(self, obj):
        return obj.trips.count()
    trip_count.short_description = 'Trips'

    def avg_score(self, obj):
        avg = obj.trips.aggregate(Avg('overall_score'))['overall_score__avg']
        return f"{avg:.1f}" if avg else "N/A"
    avg_score.short_description = 'Avg Score'

    def discount_progress(self, obj):
        return format_html(
            '<progress value="{}" max="30" style="width:100%"></progress> {}%',
            obj.total_discount * 100,
            obj.total_discount * 100
        )
    discount_progress.short_description = 'Discount Progress'

    def recalculate_discounts(self, request, queryset):
        for profile in queryset:
            profile.update_discounts()
        self.message_user(request, f"Recalculated discounts for {queryset.count()} drivers")
    recalculate_discounts.short_description = "Recalculate discounts for selected drivers"

@admin.register(DrivingTrip)
class DrivingTripAdmin(admin.ModelAdmin):
    list_display = ('driver_info', 'trip_duration', 'distance', 'speed_metrics', 'safety_scores', 'overall_score_bar')
    list_filter = ('start_time', 'night_driving')
    search_fields = ('driver__user__username', 'driver__policy_number')
    date_hierarchy = 'start_time'
    readonly_fields = ('overall_score', 'score_breakdown')
    
    fieldsets = (
        ('Trip Information', {
            'fields': ('driver', 'start_time', 'end_time', 'distance_miles')
        }),
        ('Driving Metrics', {
            'fields': ('average_speed', 'max_speed', 'hard_brakes', 'rapid_accelerations', 'night_driving')
        }),
        ('Safety Scores', {
            'fields': ('speed_score', 'braking_score', 'acceleration_score', 'overall_score', 'score_breakdown')
        }),
    )

    def driver_info(self, obj):
        return f"{obj.driver.user.get_full_name()} ({obj.driver.policy_number})"
    driver_info.short_description = 'Driver'
    driver_info.admin_order_field = 'driver__user__first_name'

    def trip_duration(self, obj):
        duration = obj.end_time - obj.start_time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    trip_duration.short_description = 'Duration'

    def distance(self, obj):
        return f"{obj.distance_miles:.1f} mi"
    distance.short_description = 'Distance'

    def speed_metrics(self, obj):
        return f"Avg: {obj.average_speed:.1f} | Max: {obj.max_speed:.1f}"
    speed_metrics.short_description = 'Speed (mph)'

    def safety_scores(self, obj):
        return f"Speed: {obj.speed_score:.1f} | Brake: {obj.braking_score:.1f} | Accel: {obj.acceleration_score:.1f}"
    safety_scores.short_description = 'Scores'

    def overall_score_bar(self, obj):
        color = "green" if obj.overall_score >= 80 else "orange" if obj.overall_score >= 60 else "red"
        return format_html(
            '<div style="background:{}; width:{}%; height:20px; color:white; text-align:center;">{:.1f}</div>',
            color, obj.overall_score, obj.overall_score
        )
    overall_score_bar.short_description = 'Overall Score'

    def score_breakdown(self, obj):
        return format_html("""
            <div style="width:100%; background:#f0f0f0; border-radius:5px; padding:5px;">
                <div style="width:{}%; background:#4CAF50; height:20px; border-radius:3px;"></div>
                <small>Speed: {:.1f}</small><br>
                <div style="width:{}%; background:#2196F3; height:20px; border-radius:3px;"></div>
                <small>Braking: {:.1f}</small><br>
                <div style="width:{}%; background:#FF9800; height:20px; border-radius:3px;"></div>
                <small>Acceleration: {:.1f}</small>
            </div>
        """,
        obj.speed_score, obj.speed_score,
        obj.braking_score, obj.braking_score,
        obj.acceleration_score, obj.acceleration_score)
    score_breakdown.short_description = 'Score Visualization'

@admin.register(DiscountHistory)
class DiscountHistoryAdmin(admin.ModelAdmin):
    list_display = ('driver_info', 'date', 'discount_breakdown', 'total_discount_display')
    list_filter = ('date',)
    search_fields = ('driver__user__username', 'driver__policy_number')
    date_hierarchy = 'date'
    readonly_fields = ('date', 'participation_discount', 'driving_discount', 'total_discount')

    def driver_info(self, obj):
        return f"{obj.driver.user.get_full_name()} ({obj.driver.policy_number})"
    driver_info.short_description = 'Driver'
    driver_info.admin_order_field = 'driver__user__first_name'

    def discount_breakdown(self, obj):
        return f"Participation: {obj.participation_discount*100:.1f}% + Driving: {obj.driving_discount*100:.1f}%"
    discount_breakdown.short_description = 'Discount Components'

    def total_discount_display(self, obj):
        return f"{obj.total_discount*100:.1f}%"
    total_discount_display.short_description = 'Total Discount'

# ===== User Admin Customization =====
class CustomUserAdmin(UserAdmin):
    inlines = (DriverProfileInline,)
    list_display = ('username', 'email', 'full_name', 'has_driver_profile', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'
    
    def has_driver_profile(self, obj):
        return hasattr(obj, 'driverprofile')
    has_driver_profile.boolean = True
    has_driver_profile.short_description = 'Has Profile'

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)