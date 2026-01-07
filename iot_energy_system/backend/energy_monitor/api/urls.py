"""
URL routing for API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeviceViewSet, SensorReadingViewSet, ThresholdViewSet,
    AlertViewSet, TicketViewSet, DashboardViewSet, ReportViewSet,
    UserViewSet
)

router = DefaultRouter()
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'readings', SensorReadingViewSet, basename='reading')
router.register(r'thresholds', ThresholdViewSet, basename='threshold')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
