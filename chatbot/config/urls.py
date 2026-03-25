from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/memory/", include("apps.memory.urls")),
    path("api/knowledge/", include("apps.knowledge.urls")),
    # Uptime ping endpoint — keeps Render + Supabase alive
    path("ping/", include("apps.chat.ping_urls")),
]