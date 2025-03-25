
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bbi_app.urls')),
    path('api/', include('bbi_api.urls')),
    
]
