"""
Report Service - Handles report generation and export.
"""

import logging
from datetime import datetime, timedelta
from django.db.models import Avg, Sum, Max, Count, Q
from django.utils import timezone
from energy_monitor.models import SensorReading, Alert, Device
import pandas as pd
from io import BytesIO

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating reports and analytics."""
    
    def generate_hourly_report(self, device_id=None):
        """Generate report for the last hour."""
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=1)
        
        return self._generate_report(
            start_time, end_time, 'hourly', device_id
        )
    
    def generate_daily_report(self, device_id=None, date_str=None):
        """Generate report for a specific day or today."""
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            end_time = timezone.make_aware(datetime.combine(date, datetime.max.time()))
        else:
            today = timezone.now().date()
            start_time = timezone.make_aware(datetime.combine(today, datetime.min.time()))
            end_time = timezone.now()
        
        return self._generate_report(
            start_time, end_time, 'daily', device_id
        )
    
    def generate_weekly_report(self, device_id=None):
        """Generate report for the last 7 days."""
        end_time = timezone.now()
        start_time = end_time - timedelta(days=7)
        
        return self._generate_report(
            start_time, end_time, 'weekly', device_id
        )
    
    def generate_monthly_report(self, device_id=None):
        """Generate report for the last 30 days."""
        end_time = timezone.now()
        start_time = end_time - timedelta(days=30)
        
        return self._generate_report(
            start_time, end_time, 'monthly', device_id
        )
    
    def _generate_report(self, start_time, end_time, report_type, device_id=None):
        """Generate report with aggregated data."""
        
        # Filter readings
        queryset = SensorReading.objects.filter(
            timestamp__gte=start_time,
            timestamp__lte=end_time
        )
        
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        # Aggregate data
        aggregates = queryset.aggregate(
            total_consumption=Sum('energy_kwh'),
            peak_power=Max('power'),
            avg_temperature=Avg('temperature'),
            avg_humidity=Avg('humidity'),
            readings_count=Count('id')
        )
        
        # Period-wise consumption
        day_consumption = queryset.filter(period_type='day').aggregate(
            total=Sum('energy_kwh')
        )['total'] or 0.0
        
        night_consumption = queryset.filter(period_type='night').aggregate(
            total=Sum('energy_kwh')
        )['total'] or 0.0
        
        holiday_consumption = queryset.filter(period_type='holiday').aggregate(
            total=Sum('energy_kwh')
        )['total'] or 0.0
        
        # Count alerts
        alert_queryset = Alert.objects.filter(
            created_at__gte=start_time,
            created_at__lte=end_time
        )
        
        if device_id:
            alert_queryset = alert_queryset.filter(device__device_id=device_id)
        
        total_alerts = alert_queryset.count()
        
        report_data = {
            'report_type': report_type,
            'start_date': start_time,
            'end_date': end_time,
            'total_consumption': aggregates['total_consumption'] or 0.0,
            'peak_power': aggregates['peak_power'] or 0.0,
            'avg_temperature': aggregates['avg_temperature'] or 0.0,
            'avg_humidity': aggregates['avg_humidity'] or 0.0,
            'total_alerts': total_alerts,
            'day_consumption': day_consumption,
            'night_consumption': night_consumption,
            'holiday_consumption': holiday_consumption,
            'readings_count': aggregates['readings_count'] or 0,
        }
        
        logger.info(f"Generated {report_type} report: {report_data['total_consumption']} kWh")
        
        return report_data
    
    def export_csv(self, report_type, device_id=None):
        """Export report data as CSV."""
        
        if report_type == 'hourly':
            report_data = self.generate_hourly_report(device_id)
        elif report_type == 'daily':
            report_data = self.generate_daily_report(device_id)
        elif report_type == 'weekly':
            report_data = self.generate_weekly_report(device_id)
        else:
            report_data = self.generate_monthly_report(device_id)
        
        # Get detailed readings for CSV
        start_time = report_data['start_date']
        end_time = report_data['end_date']
        
        queryset = SensorReading.objects.filter(
            timestamp__gte=start_time,
            timestamp__lte=end_time
        ).select_related('device')
        
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        # Convert to DataFrame
        data = list(queryset.values(
            'device__device_id', 'device__name', 'timestamp',
            'voltage', 'current', 'power', 'energy_kwh',
            'temperature', 'humidity', 'period_type'
        ))
        
        df = pd.DataFrame(data)
        
        # Rename columns
        df.columns = [
            'Device ID', 'Device Name', 'Timestamp',
            'Voltage (V)', 'Current (A)', 'Power (W)', 'Energy (kWh)',
            'Temperature (°C)', 'Humidity (%)', 'Period Type'
        ]
        
        # Create CSV buffer
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        return csv_buffer.getvalue()
    
    def export_pdf(self, report_type, device_id=None):
        """Export report as PDF."""
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        
        if report_type == 'hourly':
            report_data = self.generate_hourly_report(device_id)
        elif report_type == 'daily':
            report_data = self.generate_daily_report(device_id)
        elif report_type == 'weekly':
            report_data = self.generate_weekly_report(device_id)
        else:
            report_data = self.generate_monthly_report(device_id)
        
        # Create PDF buffer
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
        )
        
        title = Paragraph(
            f"IoT Energy Monitoring System<br/>{report_type.title()} Report",
            title_style
        )
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Report period
        period_text = f"Period: {report_data['start_date'].strftime('%Y-%m-%d %H:%M')} to {report_data['end_date'].strftime('%Y-%m-%d %H:%M')}"
        elements.append(Paragraph(period_text, styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Energy Consumption', f"{report_data['total_consumption']:.2f} kWh"],
            ['Peak Power', f"{report_data['peak_power']:.2f} W"],
            ['Average Temperature', f"{report_data['avg_temperature']:.2f} °C"],
            ['Average Humidity', f"{report_data['avg_humidity']:.2f} %"],
            ['Total Alerts', str(report_data['total_alerts'])],
            ['Number of Readings', str(report_data['readings_count'])],
        ]
        
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Period-wise consumption
        elements.append(Paragraph("Energy Consumption by Period", styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))
        
        period_data = [
            ['Period', 'Consumption (kWh)'],
            ['Day Time', f"{report_data['day_consumption']:.2f}"],
            ['Night Time', f"{report_data['night_consumption']:.2f}"],
            ['Holiday', f"{report_data['holiday_consumption']:.2f}"],
        ]
        
        period_table = Table(period_data, colWidths=[2.5 * inch, 2.5 * inch])
        period_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(period_table)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
