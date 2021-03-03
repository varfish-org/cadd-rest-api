from django.conf import settings
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls.static import static

urlpatterns = [url(r"", include("restapi.urls"))] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
