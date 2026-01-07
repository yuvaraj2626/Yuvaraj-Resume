"""
Email Service - Handles email notifications for alerts.
"""

import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from energy_monitor.models import Alert

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""
    
    def send_alert_email(self, alert: Alert):
        """Send email notification for an alert."""
        
        if not settings.ALERT_EMAIL_RECIPIENTS:
            logger.warning("No email recipients configured for alerts")
            return
        
        subject = self._generate_email_subject(alert)
        message = self._generate_email_body(alert)
        html_message = self._generate_html_email_body(alert)
        
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=settings.ALERT_EMAIL_RECIPIENTS
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Alert email sent for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise
    
    def _generate_email_subject(self, alert: Alert) -> str:
        """Generate email subject line."""
        severity_prefix = {
            'critical': '🔴 CRITICAL',
            'warning': '⚠️ WARNING',
            'info': 'ℹ️ INFO'
        }
        
        prefix = severity_prefix.get(alert.severity, '⚠️')
        return f"{prefix} - Alert: {alert.parameter_name} violation on {alert.device.device_id}"
    
    def _generate_email_body(self, alert: Alert) -> str:
        """Generate plain text email body."""
        
        return f"""
IoT Energy Monitoring System - Alert Notification

Alert Details:
--------------
Device ID: {alert.device.device_id}
Device Name: {alert.device.name}
Location: {alert.device.location}

Parameter: {alert.parameter_name}
Threshold Value: {alert.threshold_value}
Current Value: {alert.actual_value}
Violation Type: {alert.violation_type.title()}
Severity: {alert.severity.upper()}

Message: {alert.message}

Timestamp: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Please take appropriate action to resolve this issue.

---
This is an automated message from IoT Energy Monitoring System.
        """
    
    def _generate_html_email_body(self, alert: Alert) -> str:
        """Generate HTML email body."""
        
        severity_colors = {
            'critical': '#dc2626',
            'warning': '#f59e0b',
            'info': '#3b82f6'
        }
        
        color = severity_colors.get(alert.severity, '#6b7280')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: {color};
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f9fafb;
            padding: 20px;
            border: 1px solid #e5e7eb;
        }}
        .detail-row {{
            padding: 10px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        .detail-label {{
            font-weight: bold;
            display: inline-block;
            width: 150px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6b7280;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>⚠️ IoT Energy System Alert</h2>
            <p style="margin: 0; font-size: 18px;">{alert.severity.upper()} Alert</p>
        </div>
        <div class="content">
            <div class="detail-row">
                <span class="detail-label">Device ID:</span>
                <span>{alert.device.device_id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Device Name:</span>
                <span>{alert.device.name}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Location:</span>
                <span>{alert.device.location}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Parameter:</span>
                <span>{alert.parameter_name}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Threshold Value:</span>
                <span>{alert.threshold_value}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Current Value:</span>
                <span style="color: {color}; font-weight: bold;">{alert.actual_value}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Violation Type:</span>
                <span>{alert.violation_type.title()}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Timestamp:</span>
                <span>{alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
            </div>
            <div style="margin-top: 20px; padding: 15px; background-color: white; border-left: 4px solid {color};">
                <strong>Message:</strong><br>
                {alert.message}
            </div>
        </div>
        <div class="footer">
            <p>This is an automated message from IoT Energy Monitoring System.</p>
            <p>Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
