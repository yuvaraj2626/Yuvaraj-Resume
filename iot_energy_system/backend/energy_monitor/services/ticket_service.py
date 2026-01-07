"""
Ticket Service - Handles automatic ticket creation and management.
"""

import logging
from datetime import datetime
from django.db import transaction
from energy_monitor.models import Ticket, Alert

logger = logging.getLogger(__name__)


class TicketService:
    """Service for managing support tickets."""
    
    def generate_ticket_id(self) -> str:
        """Generate unique ticket ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        count = Ticket.objects.filter(ticket_id__startswith=f'TKT-{timestamp[:8]}').count()
        return f'TKT-{timestamp}-{count + 1:04d}'
    
    @transaction.atomic
    def create_alert_ticket(self, alert: Alert) -> Ticket:
        """Automatically create a ticket from an alert."""
        
        # Check if ticket already exists for this alert
        existing_ticket = Ticket.objects.filter(alert=alert).first()
        if existing_ticket:
            logger.info(f"Ticket already exists for alert {alert.id}: {existing_ticket.ticket_id}")
            return existing_ticket
        
        ticket_id = self.generate_ticket_id()
        issue_type = f"{alert.parameter_name.upper()} Threshold Violation"
        
        description = self._generate_ticket_description(alert)
        
        # Map alert severity to ticket severity
        severity_mapping = {
            'critical': 'critical',
            'warning': 'high',
            'info': 'medium'
        }
        severity = severity_mapping.get(alert.severity, 'medium')
        
        ticket = Ticket.objects.create(
            ticket_id=ticket_id,
            device=alert.device,
            alert=alert,
            issue_type=issue_type,
            description=description,
            severity=severity,
            status='open'
        )
        
        logger.info(f"Ticket created: {ticket.ticket_id} for alert {alert.id}")
        
        return ticket
    
    def _generate_ticket_description(self, alert: Alert) -> str:
        """Generate ticket description from alert."""
        
        return f"""
Automated Ticket: Threshold Violation Detected

Device Information:
- Device ID: {alert.device.device_id}
- Device Name: {alert.device.name}
- Location: {alert.device.location}

Alert Details:
- Parameter: {alert.parameter_name}
- Threshold Value: {alert.threshold_value}
- Actual Value: {alert.actual_value}
- Violation Type: {alert.violation_type.title()}
- Severity: {alert.severity.upper()}

Alert Message:
{alert.message}

Alert Timestamp: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Action Required:
Please investigate the cause of this threshold violation and take corrective action.
        """.strip()
    
    def update_ticket_status(self, ticket_id: str, status: str, resolution_notes: str = None):
        """Update ticket status."""
        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)
            ticket.status = status
            
            if resolution_notes:
                ticket.resolution_notes = resolution_notes
            
            if status in ['resolved', 'closed']:
                ticket.resolved_at = datetime.now()
            
            ticket.save()
            logger.info(f"Ticket {ticket_id} status updated to {status}")
            
        except Ticket.DoesNotExist:
            logger.error(f"Ticket {ticket_id} not found")
            raise
