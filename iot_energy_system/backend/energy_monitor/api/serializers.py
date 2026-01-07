"""
Serializers for REST API.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from energy_monitor.models import (
    Device, SensorReading, Threshold, Alert, Ticket, AuditLog
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'first_name', 'last_name']
        read_only_fields = ['id']


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model."""
    
    class Meta:
        model = Device
        fields = [
            'id', 'device_id', 'name', 'location', 'device_type', 
            'status', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SensorReadingSerializer(serializers.ModelSerializer):
    """Serializer for SensorReading model."""
    
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = SensorReading
        fields = [
            'id', 'device', 'device_id', 'device_name', 'timestamp',
            'voltage', 'current', 'power', 'energy_kwh',
            'temperature', 'humidity', 'period_type', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SensorReadingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sensor readings with device_id."""
    
    device_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = SensorReading
        fields = [
            'device_id', 'timestamp', 'voltage', 'current', 'power', 
            'energy_kwh', 'temperature', 'humidity', 'period_type'
        ]
    
    def create(self, validated_data):
        device_id = validated_data.pop('device_id')
        device = Device.objects.get(device_id=device_id)
        validated_data['device'] = device
        return super().create(validated_data)


class ThresholdSerializer(serializers.ModelSerializer):
    """Serializer for Threshold model."""
    
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = Threshold
        fields = [
            'id', 'device', 'device_id', 'device_name', 'parameter_name',
            'upper_limit', 'lower_limit', 'enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate threshold limits."""
        upper_limit = data.get('upper_limit')
        lower_limit = data.get('lower_limit')
        
        if upper_limit is not None and lower_limit is not None:
            if upper_limit <= lower_limit:
                raise serializers.ValidationError(
                    "Upper limit must be greater than lower limit."
                )
        
        return data


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model."""
    
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    acknowledged_by_username = serializers.CharField(
        source='acknowledged_by.username', 
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Alert
        fields = [
            'id', 'device', 'device_id', 'device_name', 'reading', 'threshold',
            'parameter_name', 'threshold_value', 'actual_value',
            'violation_type', 'severity', 'status', 'message',
            'acknowledged_by', 'acknowledged_by_username', 'acknowledged_at',
            'created_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for Ticket model."""
    
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    assigned_to_username = serializers.CharField(
        source='assigned_to.username',
        read_only=True,
        allow_null=True
    )
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_id', 'device', 'device_id', 'device_name', 'alert',
            'issue_type', 'description', 'severity', 'status',
            'assigned_to', 'assigned_to_username',
            'created_by', 'created_by_username',
            'created_at', 'updated_at', 'resolved_at', 'resolution_notes'
        ]
        read_only_fields = ['id', 'ticket_id', 'created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    
    username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'username', 'action', 'entity_type', 'entity_id',
            'timestamp', 'details', 'ip_address'
        ]
        read_only_fields = ['id', 'timestamp']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    
    total_devices = serializers.IntegerField()
    active_devices = serializers.IntegerField()
    total_readings_today = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    total_energy_today = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    avg_humidity = serializers.FloatField()


class ReportSerializer(serializers.Serializer):
    """Serializer for report data."""
    
    report_type = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    total_consumption = serializers.FloatField()
    peak_power = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    avg_humidity = serializers.FloatField()
    total_alerts = serializers.IntegerField()
    day_consumption = serializers.FloatField()
    night_consumption = serializers.FloatField()
    holiday_consumption = serializers.FloatField()
    readings_count = serializers.IntegerField()
