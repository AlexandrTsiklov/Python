from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from TXPR import settings

urlpatterns = [
    path('app/admin/', admin.site.urls),
    path('app/', include('users.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

