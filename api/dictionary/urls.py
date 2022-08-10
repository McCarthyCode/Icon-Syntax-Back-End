from django.urls import re_path, include
from rest_framework.routers import SimpleRouter

from .views import *
from .viewsets import *

app_name = 'api.dictionary'

urlpatterns = [
    re_path(
        r'^icons/(?P<id>[1-9]\d*)/approve$',
        IconApproveView.as_view(),
        name='icon-approve'),
    re_path(
        r'^audio/(?P<id>[a-z0-9\W_]+)\.mp3$',
        MP3RetrieveView.as_view(),
        name='audio'),
]

categories_router = SimpleRouter(trailing_slash=False)
categories_router.register(r'^categories', CategoriesViewSet)

icons_router = SimpleRouter(trailing_slash=False)
icons_router.register(r'^icons', IconsViewSet)

urlpatterns += categories_router.urls
urlpatterns += icons_router.urls
