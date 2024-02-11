from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from config import swagger


admin.site.site_url = None


urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += swagger.urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)