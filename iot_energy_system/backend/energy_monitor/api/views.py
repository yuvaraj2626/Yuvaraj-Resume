"""
API Views for IoT Energy Monitoring System.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Sum, Max, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from energy_monitor.models import (
    Device, SensorReading, Threshold, Alert, Ticket, AuditLog
)
from .serializers import (
    DeviceSerializer, SensorReadingSerializer, SensorReadingCreateSerializer,
    ThresholdSerializer, AlertSerializer, TicketSerializer, AuditLogSerializer,
    DashboardStatsSerializer, ReportSerializer, UserSerializer
)
from energy_monitor.services.alert_service import AlertService
from energy_monitor.services.ticket_service import TicketService
from energy_monitor.services.report_service import ReportService

User = get_user_model()


class DeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for Device CRUD operations."""
    
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'device_type']
    search_fields = ['device_id', 'name', 'location']
    ordering_fields = ['created_at', 'name']
    
    @action(detail=True, methods=['get'])
    def latest_reading(self, request, pk=None):
        """Get the latest sensor reading for a device."""
        device = self.get_object()
        reading = device.readings.first()
        if reading:
            serializer = SensorReadingSerializer(reading)
            return Response(serializer.data)
        return Response({'detail': 'No readings found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for a specific device."""
        device = self.get_object()
        
        # Get time range (default: last 24 hours)
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        stats = device.readings.filter(timestamp__gte=since).aggregate(
            total_energy=Sum('energy_kwh'),
            avg_power=Avg('power'),
            max_power=Max('power'),
            avg_temperature=Avg('temperature'),
            avg_humidity=Avg('humidity'),
            readings_count=Count('id')
        )
        
        return Response(stats)


class SensorReadingViewSet(viewsets.ModelViewSet):
    """ViewSet for SensorReading operations."""
    
    queryset = SensorReading.objects.select_related('device').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device', 'period_type']
    ordering_fields = ['timestamp']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SensorReadingCreateSerializer
        return SensorReadingSerializer
    
    def create(self, request, *args, **kwargs):
        """Create new sensor reading and check thresholds."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reading = serializer.save()
        
        # Check thresholds and create alerts if needed
        alert_service = AlertService()
        alerts = alert_service.check_thresholds(reading)
        
        response_serializer = SensorReadingSerializer(reading)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest readings for all devices."""
        devices = Device.objects.filter(status='active')
        latest_readings = []
        
        for device in devices:
            reading = device.readings.first()
            if reading:
                latest_readings.append(reading)
        
        serializer = self.get_serializer(latest_readings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def time_series(self, request):
        """Get time series data for charting."""
        device_id = request.query_params.get('device_id')
        hours = int(request.query_params.get('hours', 24))
        parameter = request.query_params.get('parameter', 'power')
        
        since = timezone.now() - timedelta(hours=hours)
        
        queryset = self.queryset.filter(timestamp__gte=since)
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        queryset = queryset.order_by('timestamp')
        
        data = list(queryset.values('timestamp', parameter, 'device__device_id'))
        return Response(data)


class ThresholdViewSet(viewsets.ModelViewSet):
    """ViewSet for Threshold configuration."""
    
    queryset = Threshold.objects.select_related('device').all()
    serializer_class = ThresholdSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['device', 'parameter_name', 'enabled']
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle threshold enabled/disabled."""
        threshold = self.get_object()
        threshold.enabled = not threshold.enabled
        threshold.save()
        
        serializer = self.get_serializer(threshold)
        return Response(serializer.data)


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet for Alert management."""
    
    queryset = Alert.objects.select_related('device', 'reading', 'threshold').all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device', 'severity', 'status', 'parameter_name']
    ordering_fields = ['created_at', 'severity']
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert."""
        alert = self.get_object()
        alert.status = 'acknowledged'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        # Log audit
        AuditLog.objects.create(
            user=request.user,
            action='alert_acknowledge',
            entity_type='alert',
            entity_id=alert.id,
            details={'alert_id': alert.id}
        )
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert."""
        alert = self.get_object()
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active alerts."""
        alerts = self.queryset.filter(status='active').order_by('-created_at')
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet for Ticket management."""
    
    queryset = Ticket.objects.select_related('device', 'alert', 'assigned_to', 'created_by').all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device', 'severity', 'status']
    ordering_fields = ['created_at', 'severity']
    
    def perform_create(self, serializer):
        """Set created_by and generate ticket_id."""
        ticket_service = TicketService()
        ticket_id = ticket_service.generate_ticket_id()
        serializer.save(created_by=self.request.user, ticket_id=ticket_id)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update ticket status."""
        ticket = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Ticket.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.status = new_status
        
        if new_status in ['resolved', 'closed']:
            ticket.resolved_at = timezone.now()
        
        ticket.save()
        
        # Log audit
        AuditLog.objects.create(
            user=request.user,
            action='ticket_update',
            entity_type='ticket',
            entity_id=ticket.id,
            details={
                'ticket_id': ticket.ticket_id,
                'old_status': ticket.status,
                'new_status': new_status
            }
        )
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign ticket to a user."""
        ticket = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            ticket.assigned_to = user
            ticket.status = 'in_progress'
            ticket.save()
            
            serializer = self.get_serializer(ticket)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for dashboard statistics and data."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics."""
        today = timezone.now().date()
        
        stats = {
            'total_devices': Device.objects.count(),
            'active_devices': Device.objects.filter(status='active').count(),
            'total_readings_today': SensorReading.objects.filter(
                timestamp__date=today
            ).count(),
            'active_alerts': Alert.objects.filter(status='active').count(),
            'open_tickets': Ticket.objects.filter(
                status__in=['open', 'in_progress']
            ).count(),
        }
        
        # Energy consumption today
        energy_today = SensorReading.objects.filter(
            timestamp__date=today
        ).aggregate(total=Sum('energy_kwh'))
        stats['total_energy_today'] = energy_today['total'] or 0.0
        
        # Average temperature and humidity today
        env_stats = SensorReading.objects.filter(
            timestamp__date=today
        ).aggregate(
            avg_temp=Avg('temperature'),
            avg_humidity=Avg('humidity')
        )
        stats['avg_temperature'] = env_stats['avg_temp'] or 0.0
        stats['avg_humidity'] = env_stats['avg_humidity'] or 0.0
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)


class ReportViewSet(viewsets.ViewSet):
    """ViewSet for report generation."""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.report_service = ReportService()
    
    @action(detail=False, methods=['get'])
    def hourly(self, request):
        """Generate hourly report."""
        device_id = request.query_params.get('device_id')
        report_data = self.report_service.generate_hourly_report(device_id)
        serializer = ReportSerializer(report_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Generate daily report."""
        device_id = request.query_params.get('device_id')
        date_str = request.query_params.get('date')
        report_data = self.report_service.generate_daily_report(device_id, date_str)
        serializer = ReportSerializer(report_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def weekly(self, request):
        """Generate weekly report."""
        device_id = request.query_params.get('device_id')
        report_data = self.report_service.generate_weekly_report(device_id)
        serializer = ReportSerializer(report_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def monthly(self, request):
        """Generate monthly report."""
        device_id = request.query_params.get('device_id')
        report_data = self.report_service.generate_monthly_report(device_id)
        serializer = ReportSerializer(report_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """Export report as PDF."""
        report_type = request.query_params.get('type', 'daily')
        device_id = request.query_params.get('device_id')
        
        pdf_file = self.report_service.export_pdf(report_type, device_id)
        
        response = Response(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{report_type}.pdf"'
        return response
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export report as CSV."""
        report_type = request.query_params.get('type', 'daily')
        device_id = request.query_params.get('device_id')
        
        csv_file = self.report_service.export_csv(report_type, device_id)
        
        response = Response(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="report_{report_type}.csv"'
        return response


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for User operations."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
