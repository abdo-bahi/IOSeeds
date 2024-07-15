from django.contrib import admin
from .models import User, SensorData, Action, MCU

# Register your models here.

admin.site.register(SensorData)
admin.site.register(Action)
admin.site.register(MCU)
admin.site.register(User)
