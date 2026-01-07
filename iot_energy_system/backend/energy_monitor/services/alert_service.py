"""
Alert Service - Handles threshold monitoring and alert creation.
"""

import logging
from typing import List
from django.db import transaction
from energy_monitor.models import Alert, Threshold, SensorReading
from .email_service import EmailService
from .ticket_service import TicketService

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing alerts and threshold violations."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.ticket_service = TicketService()
    
    def check_thresholds(self, reading: SensorReading) -> List[Alert]:
        """
        Check sensor reading against all thresholds for the device.
        Create alerts for violations and trigger notifications.
        """
        alerts = []
        thresholds = Threshold.objects.filter(
            device=reading.device,
            enabled=True
        )
        
        for threshold in thresholds:
            alert = self._check_single_threshold(reading, threshold)
            if alert:
                alerts.append(alert)
                
                # Send email notification
                try:
                    self.email_service.send_alert_email(alert)
                except Exception as e:
                    logger.error(f"Failed to send alert email: {e}")
                
                # Create ticket for critical alerts
                if alert.severity == 'critical':
                    try:
                        self.ticket_service.create_alert_ticket(alert)
                    except Exception as e:
                        logger.error(f"Failed to create ticket: {e}")
        
        return alerts
    
    def _check_single_threshold(self, reading: SensorReading, threshold: Threshold) -> Alert:
        """Check a single threshold against the reading."""
        parameter_value = getattr(reading, threshold.parameter_name)
        
        # Check upper limit violation
        if threshold.upper_limit is not None and parameter_value > threshold.upper_limit:
            return self._create_alert(
                reading=reading,
                threshold=threshold,
                actual_value=parameter_value,
                violation_type='upper'
            )
        
        # Check lower limit violation
        if threshold.lower_limit is not None and parameter_value < threshold.lower_limit:
            return self._create_alert(
                reading=reading,
                threshold=threshold,
                actual_value=parameter_value,
                violation_type='lower'
            )
        
        return None
    
    @transaction.atomic
    def _create_alert(self, reading: SensorReading, threshold: Threshold, 
                     actual_value: float, violation_type: str) -> Alert:
        """Create an alert record."""
        
        # Determine severity based on violation magnitude
        threshold_value = (threshold.upper_limit if violation_type == 'upper' 
                          else threshold.lower_limit)
        
        deviation_percent = abs((actual_value - threshold_value) / threshold_value * 100)
        
        if deviation_percent > 50:
            severity = 'critical'
        elif deviation_percent > 20:
            severity = 'warning'
        else:
            severity = 'info'
        
        # Create alert message
        message = self._generate_alert_message(
            device_id=reading.device.device_id,
            parameter=threshold.parameter_name,
            actual_value=actual_value,
            threshold_value=threshold_value,
            violation_type=violation_type
        )
        
        alert = Alert.objects.create(
            device=reading.device,
            reading=reading,
            threshold=threshold,
            parameter_name=threshold.parameter_name,
            threshold_value=threshold_value,
            actual_value=actual_value,
            violation_type=violation_type,
            severity=severity,
            message=message
        )
        
        logger.info(f"Alert created: {alert.id} - {alert.severity} - {message}")
        
        return alert
    
    def _generate_alert_message(self, device_id: str, parameter: str, 
                                actual_value: float, threshold_value: float,
                                violation_type: str) -> str:
        """Generate human-readable alert message."""
        
        parameter_display = {
            'voltage': 'Voltage',
            'current': 'Current',
            'power': 'Power',
            'energy_kwh': 'Energy',
            'temperature': 'Temperature',
            'humidity': 'Humidity'
        }
        
        param_name = parameter_display.get(parameter, parameter)
        
        if violation_type == 'upper':
            return (f"{param_name} exceeded threshold for device {device_id}. "
                   f"Current value: {actual_value:.2f}, Threshold: {threshold_value:.2f}")
        else:
            return (f"{param_name} below threshold for device {device_id}. "
                   f"Current value: {actual_value:.2f}, Threshold: {threshold_value:.2f}")
    
    def resolve_alert(self, alert_id: int):
        """Resolve an alert."""
        try:
            alert = Alert.objects.get(id=alert_id)
            alert.status = 'resolved'
            alert.save()
            logger.info(f"Alert {alert_id} resolved")
        except Alert.DoesNotExist:
            logger.error(f"Alert {alert_id} not found")
