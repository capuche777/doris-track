"""URL configuration for DorisTrack."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.dashboard.urls")),
    path("", include("apps.profiles.urls")),
    path("scores/", include("apps.scores.urls")),
    path("vocabulary/", include("apps.vocabulary.urls")),
    path("quiz/", include("apps.quiz.urls")),
    path("grammar/", include("apps.grammar.urls")),
    path("practice/", include("apps.practice.urls")),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += debug_toolbar_urls()