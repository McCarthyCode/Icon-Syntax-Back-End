from rest_framework.routers import SimpleRouter
from django.urls import re_path, include
from .viewsets import PDFViewSet

app_name = 'api.pdf'
router = SimpleRouter(trailing_slash=False)
router.register(r'^pdf', PDFViewSet)

urlpatterns = router.urls
