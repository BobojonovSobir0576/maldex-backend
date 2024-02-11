from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import path


schema_view = get_schema_view(
    openapi.Info(
        title="Test",
        default_version="v1",
        description="Test",
    ),
    public=True,
    permission_classes=(permissions.AllowAny),
)

urlpatterns = [
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui",),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", TemplateView.as_view(template_name="doc.html", extra_context={"schema_url": "api_schema"}), name="swagger-ui",),
]