
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Set the site URL for the Django admin panel to None
admin.site.site_url = None

# Define the schema view for generating API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Maldex Backend",
        default_version="v1",
        description="Maldex Backend",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Define the urlpatterns for the Django application
urlpatterns = [
    # Swagger UI and schema paths
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # CKEditor 5 URL for uploading files
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),

    # Admin panel URL
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('auth/', include('apps.auth_app.urls')),

    # Product URLs
    path('product/', include('apps.product.urls')),

    # Banner URLs
    path('banner/', include('apps.banner.urls')),

    # Gifts Baskets URLs
    path('gifts/baskets/', include('apps.gifts_baskets.urls')),

    # Blog URLs
    path('', include('apps.blog.urls')),
]

# Add static URLs for serving static files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add media URLs for serving media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Define a media URL pattern for serving media files using Django's serve function
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
    ),
]
