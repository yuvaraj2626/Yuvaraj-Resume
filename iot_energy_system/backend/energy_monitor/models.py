"""
Database models for IoT Energy Monitoring System.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class User(AbstractUser):
    """Extended user model with role-based access control."""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('viewer', 'Viewer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return f"{self.username} ({self.role})"


class Device(models.Model):
    """IoT energy meter device."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    DEVICE_TYPE_CHOICES = [
        ('energy_meter', 'Energy Meter'),
        ('temperature_sensor', 'Temperature Sensor'),
        ('humidity_sensor', 'Humidity Sensor'),
        ('combined', 'Combined Sensor'),
    ]
    
    device_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES, default='combined')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'devices'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.device_id} - {self.name}"


class SensorReading(models.Model):
    """Time-series sensor readings from IoT devices."""
    
    PERIOD_CHOICES = [
        ('day', 'Day Time'),
        ('night', 'Night Time'),
        ('holiday', 'Holiday'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Electrical parameters
    voltage = models.FloatField(validators=[MinValueValidator(0)], help_text="Voltage in V")
    current = models.FloatField(validators=[MinValueValidator(0)], help_text="Current in A")
    power = models.FloatField(validators=[MinValueValidator(0)], help_text="Power in W")
    energy_kwh = models.FloatField(validators=[MinValueValidator(0)], help_text="Energy in kWh")
    
    # Environmental parameters
    temperature = models.FloatField(help_text="Temperature in °C")
    humidity = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Humidity in %"
    )
    
    # Time classification
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='day')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sensor_readings'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
            models.Index(fields=['period_type', '-timestamp']),
        ]
        
    def __str__(self):
        return f"{self.device.device_id} - {self.timestamp}"


class Threshold(models.Model):
    """Threshold configuration for monitoring parameters."""
    
    PARAMETER_CHOICES = [
        ('voltage', 'Voltage'),
        ('current', 'Current'),
        ('power', 'Power'),
        ('energy_kwh', 'Energy (kWh)'),
        ('temperature', 'Temperature'),
        ('humidity', 'Humidity'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='thresholds')
    parameter_name = models.CharField(max_length=50, choices=PARAMETER_CHOICES)
    upper_limit = models.FloatField(null=True, blank=True, help_text="Maximum allowed value")
    lower_limit = models.FloatField(null=True, blank=True, help_text="Minimum allowed value")
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'thresholds'
        unique_together = ['device', 'parameter_name']
        
    def __str__(self):
        return f"{self.device.device_id} - {self.parameter_name}"


class Alert(models.Model):
    """Alert records for threshold violations."""
    
    VIOLATION_TYPE_CHOICES = [
        ('upper', 'Upper Limit Exceeded'),
        ('lower', 'Lower Limit Breached'),
    ]
    
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Information'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('acknowledged', 'Acknowledged'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alerts')
    reading = models.ForeignKey(SensorReading, on_delete=models.CASCADE, related_name='alerts')
    threshold = models.ForeignKey(Threshold, on_delete=models.CASCADE, related_name='alerts')
    
    parameter_name = models.CharField(max_length=50)
    threshold_value = models.FloatField()
    actual_value = models.FloatField()
    violation_type = models.CharField(max_length=20, choices=VIOLATION_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='warning')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    message = models.TextField()
    acknowledged_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
        
    def __str__(self):
        return f"Alert #{self.id} - {self.device.device_id} - {self.severity}"


class Ticket(models.Model):
    """Support ticket for incident management."""
    
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    ticket_id = models.CharField(max_length=50, unique=True, db_index=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='tickets')
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='tickets', null=True, blank=True)
    
    issue_type = models.CharField(max_length=100)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_tickets'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tickets'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    resolution_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
        ]
        
    def __str__(self):
        return f"{self.ticket_id} - {self.issue_type}"


class AuditLog(models.Model):
    """Audit trail for security and compliance."""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('alert_acknowledge', 'Alert Acknowledged'),
        ('ticket_update', 'Ticket Updated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)
    entity_id = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['entity_type', '-timestamp']),
        ]
        
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
