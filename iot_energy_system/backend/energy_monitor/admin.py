from django.contrib import admin
from .models import Device, SensorReading, Threshold, Alert, Ticket, AuditLog

admin.site.register(Device)
admin.site.register(SensorReading)
admin.site.register(Threshold)
admin.site.register(Alert)
admin.site.register(Ticket)
admin.site.register(AuditLog)
