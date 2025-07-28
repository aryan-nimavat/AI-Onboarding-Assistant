# agents/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CallRecordingViewSet

router = DefaultRouter()
router.register(r'call-recordings', CallRecordingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]