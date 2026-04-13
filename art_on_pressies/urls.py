import os

from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path
from django.views.decorators.cache import never_cache


@never_cache
def serve_media(request, path):
    full_path = os.path.join(str(settings.MEDIA_ROOT), path)
    if os.path.isfile(full_path):
        return FileResponse(open(full_path, 'rb'))
    raise Http404()


urlpatterns = [
    path('admin/', admin.site.urls),
    path('media/<path:path>', serve_media),
    path('', include('core.urls')),
]
