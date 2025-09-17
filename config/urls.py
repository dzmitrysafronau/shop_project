import os

import redis
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def health(request):
    ok_db = ok_redis = False
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1;")
        ok_db = True
    except Exception:
        ok_db = False

    try:
        r = redis.from_url(os.getenv("REDIS_URL"))
        r.ping()
        ok_redis = True
    except Exception:
        ok_redis = False

    status_code = 200 if (ok_db and ok_redis) else 503
    return JsonResponse({"db": ok_db, "redis": ok_redis}, status=status_code)


urlpatterns = [
    path("admin/", admin.site.urls),

    # API docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),

    # Auth (JWT)
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # App routes
    path("api/", include("shop.urls")),

    # Healthcheck
    path("health/", health),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
