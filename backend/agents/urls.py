# agents/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CallRecordingViewSet, ExtractedClientInfoViewSet, ClientViewSet, get_user_status

router = DefaultRouter()
router.register(r'call-recordings', CallRecordingViewSet, basename='call-recording')
router.register(r'extracted-info', ExtractedClientInfoViewSet, basename='extracted-info')
router.register(r'clients', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
    path('user-status/', get_user_status, name='user-status'),
]