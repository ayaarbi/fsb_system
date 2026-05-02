from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('dashboard/', include('administration.urls')),
    path('pedagogie/', include('pedagogie.urls')),
    path('examens/', include('examens.urls')),
    path('stages/', include('stages.urls')),
    path('ai/', include('ai_agents.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)