# agents/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CallRecordingViewSet, ExtractedClientInfoViewSet 

router = DefaultRouter()
router.register(r'call-recordings', CallRecordingViewSet, basename='call-recording')
router.register(r'extracted-info', ExtractedClientInfoViewSet, basename='extracted-info')

urlpatterns = [
    path('', include(router.urls)),
]