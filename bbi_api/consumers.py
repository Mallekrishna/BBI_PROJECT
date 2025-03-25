import json
from channels.generic.websocket import AsyncWebsocketConsumer
from geopy.distance import geodesic
from channels.db import database_sync_to_async

class TelematicsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        await self.channel_layer.group_add(self.device_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.device_id, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        driver = await self.get_driver(self.device_id)
        
        await self.create_telematics_data(driver, data)
        await self.check_alerts(driver, data)
        await self.check_geofence(driver, data)

        await self.channel_layer.group_send(
            self.device_id,
            {'type': 'telematics.update', 'data': data}
        )

    async def telematics_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def get_driver(self, device_id):
        from bbi_app.models import DriverProfile
        return DriverProfile.objects.get(device_id=device_id)

    @database_sync_to_async
    def create_telematics_data(self, driver, data):
        from bbi_app.models import TelematicsData
        return TelematicsData.objects.create(
            driver=driver,
            speed=data['speed'],
            latitude=data['lat'],
            longitude=data['lon'],
            acceleration=data['accel'],
            brake_force=data.get('brake'),
            is_hard_brake=data.get('is_hard_brake', False)
        )

    async def check_alerts(self, driver, data):
        from bbi_app.models import Alert
        alerts = []

        if data['speed'] > 70:
            alerts.append({'type': 'speed', 'message': f"Speed exceeded: {data['speed']} mph", 'severity': 'high'})

        if data.get('is_hard_brake', False):
            alerts.append({'type': 'hard_brake', 'message': "Hard braking detected", 'severity': 'med'})

        for alert in alerts:
            await self.channel_layer.group_send(
                f"alerts_{driver.user.id}",
                {'type': 'send.alert', 'alert': alert}
            )
            await self.create_alert(driver, alert)

    @database_sync_to_async
    def create_alert(self, driver, alert):
        from bbi_app.models import Alert
        return Alert.objects.create(driver=driver, message=alert['message'], severity=alert['severity'])

    async def check_geofence(self, driver, data):
        from bbi_app.models import Geofence, GeofenceLog
        current_pos = (data['lat'], data['lon'])
        fences = await database_sync_to_async(list)(Geofence.objects.all())

        for fence in fences:
            fence_pos = (float(fence.latitude), float(fence.longitude))
            distance = geodesic(current_pos, fence_pos).meters

            if distance <= fence.radius:
                await self.create_geofence_log(driver, fence)
                if not fence.is_allowed:
                    await self.channel_layer.group_send(
                        f"alerts_{driver.user.id}",
                        {'type': 'send.alert', 'alert': {'type': 'geo', 'message': f"Entered restricted zone: {fence.name}", 'severity': 'high'}}
                    )

    @database_sync_to_async
    def create_geofence_log(self, driver, fence):
        from bbi_app.models import GeofenceLog
        return GeofenceLog.objects.create(geofence=fence, driver=driver, event_type='entry' if fence.is_allowed else 'violation')
