from django.conf.urls import url, include
from rest_framework import routers
from ocrapi.api import views as api_views
from django.conf.urls.static import static
from django.conf import settings


router = routers.DefaultRouter()
router.register(r'images', api_views.AnalyzedImageViewSet, 'images')
router.register(r'structure', api_views.StructureViewSet, 'structure')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
