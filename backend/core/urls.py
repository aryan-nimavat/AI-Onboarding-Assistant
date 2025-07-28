from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views # import views for token authentication
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')), # for login/logout in browsable API
    path('api/token/', views.obtain_auth_token), # endpoint to get auth token
    path('api/', include('agents.urls')), # including agents' urls
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)