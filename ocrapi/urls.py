from django.conf.urls import url, include
from rest_framework import routers
from ocrapi.api import views as api_views
from ocrapi.remote import views as remote_views
from django.conf.urls.static import static
from django.conf import settings


router = routers.DefaultRouter()
router.register(r'images', api_views.AnalyzedImageViewSet, 'images')
router.register(r'structure', api_views.StructureViewSet, 'structure')
router.register(r'orders', remote_views.OrderViewSet, 'orders')
router.register(r'wholesalers', remote_views.WholesalerView, 'items')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^webhook', remote_views.WebhookView.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
