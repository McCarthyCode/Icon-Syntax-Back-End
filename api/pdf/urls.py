from rest_framework.routers import SimpleRouter
from django.urls import re_path, include
from .viewsets import *

app_name = 'api.pdf'
router = SimpleRouter(trailing_slash=False)
router.register(r'^pdfs/categories', PDFCategoryViewset)
router.register(r'^pdfs', PDFViewSet)

urlpatterns = router.urls
