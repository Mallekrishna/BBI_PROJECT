from django.contrib import admin
from .models import TelematicsData, AlertRule, Alert, Geofence, GeofenceLog
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg

# ===== Telematics Data Admin =====
@admin.register(TelematicsData)
class TelematicsDataAdmin(admin.ModelAdmin):
    list_display = ('driver_info', 'timestamp', 'speed', 'acceleration', 'hard_brake_indicator')
    list_filter = ('is_hard_brake', 'timestamp')
    search_fields = ('driver__user__username', 'driver__license_number')
    date_hierarchy = 'timestamp'
    readonly_fields = ('map_preview',)
    fieldsets = (
        ('Driver Info', {
            'fields': ('driver',)
        }),
        ('Location Data', {
            'fields': ('latitude', 'longitude', 'map_preview')
        }),
        ('Vehicle Metrics', {
            'fields': ('speed', 'acceleration', 'brake_force', 'is_hard_brake', 'rpm', 'fuel_level')
        }),
    )

    def driver_info(self, obj):
        return f"{obj.driver.user.username} ({obj.driver.license_number})"
    driver_info.short_description = 'Driver'
    driver_info.admin_order_field = 'driver__user__username'

    def hard_brake_indicator(self, obj):
        return "⚠️ Hard Brake" if obj.is_hard_brake else ""
    hard_brake_indicator.short_description = 'Brake Alert'

    def map_preview(self, obj):
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="https://www.google.com/maps?q={},{}" target="_blank">'
                '<img src="https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom=14&size=400x200&maptype=roadmap&markers=color:red%7C{},{}" width="400" height="200">'
                '</a>',
                obj.latitude, obj.longitude,
                obj.latitude, obj.longitude,
                obj.latitude, obj.longitude
            )
        return "No location data"
    map_preview.short_description = 'Map Preview'

# ===== Alert System Admin =====
class AlertInline(admin.TabularInline):
    model = Alert
    extra = 0
    readonly_fields = ('timestamp', 'message', 'severity')
    fields = ('timestamp', 'rule', 'message', 'severity', 'is_read')
    ordering = ('-timestamp',)

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('rule_name', 'driver', 'alert_type', 'threshold', 'active_status', 'alert_count')
    list_filter = ('alert_type', 'is_active')
    search_fields = ('driver__user__username',)
    inlines = [AlertInline]
    actions = ['enable_rules', 'disable_rules']

    def rule_name(self, obj):
        return f"{obj.get_alert_type_display()} > {obj.threshold}"
    rule_name.short_description = 'Rule'

    def active_status(self, obj):
        return "✅ Active" if obj.is_active else "❌ Inactive"
    active_status.short_description = 'Status'

    def alert_count(self, obj):
        return obj.alert_set.count()
    alert_count.short_description = 'Alerts'

    def enable_rules(self, request, queryset):
        queryset.update(is_active=True)
    enable_rules.short_description = "Enable selected rules"

    def disable_rules(self, request, queryset):
        queryset.update(is_active=False)
    disable_rules.short_description = "Disable selected rules"

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('driver', 'alert_type', 'short_message', 'timestamp', 'severity', 'read_status')
    list_filter = ('severity', 'is_read', 'timestamp')
    search_fields = ('driver__user__username', 'message')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    actions = ['mark_as_read', 'mark_as_unread']

    def alert_type(self, obj):
        return obj.rule.get_alert_type_display()
    alert_type.short_description = 'Type'

    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message'

    def read_status(self, obj):
        return "✔ Read" if obj.is_read else "✖ Unread"
    read_status.short_description = 'Status'

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected alerts as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected alerts as unread"

# ===== Geofence Admin =====
class GeofenceLogInline(admin.TabularInline):
    model = GeofenceLog
    extra = 0
    readonly_fields = ('timestamp', 'driver', 'event_type')
    ordering = ('-timestamp',)

@admin.register(Geofence)
class GeofenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'radius', 'zone_type', 'log_count')
    list_filter = ('is_allowed',)
    search_fields = ('name',)
    inlines = [GeofenceLogInline]
    readonly_fields = ('map_preview',)

    def location(self, obj):
        return f"{obj.latitude}, {obj.longitude}"
    location.short_description = 'Coordinates'

    def zone_type(self, obj):
        return "🟢 Allowed" if obj.is_allowed else "🔴 Restricted"
    zone_type.short_description = 'Type'

    def log_count(self, obj):
        return obj.geofencelog_set.count()
    log_count.short_description = 'Events'

    def map_preview(self, obj):
        return format_html(
            '<a href="https://www.google.com/maps?q={},{}" target="_blank">'
            '<img src="https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom=12&size=400x200&maptype=roadmap&markers=color:{}%7C{},{}" width="400" height="200">'
            '</a>',
            obj.latitude, obj.longitude,
            obj.latitude, obj.longitude,
            'green' if obj.is_allowed else 'red',
            obj.latitude, obj.longitude
        )
    map_preview.short_description = 'Zone Preview'

@admin.register(GeofenceLog)
class GeofenceLogAdmin(admin.ModelAdmin):
    list_display = ('geofence', 'driver', 'event_icon', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('geofence__name', 'driver__user__username')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)

    def event_icon(self, obj):
        if obj.event_type == 'entry':
            return "⬇️ Entry" if obj.geofence.is_allowed else "⚠️ Entry"
        return "⬆️ Exit" if obj.geofence.is_allowed else "✅ Exit"
    event_icon.short_description = 'Event'