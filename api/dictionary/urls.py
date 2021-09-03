import string
from django.urls import re_path, include
from .views import *

app_name = 'api.dictionary'

urlpatterns = [
    re_path(r'^icons/upload$', IconUploadView.as_view(), name='icon-upload'),
    re_path(
        r'^icons/delete/(?P<id>[1-9]\d*)$',
        IconDeleteView.as_view(),
        name='icon-delete'),
    re_path(
        r'^icons/(?P<id>[1-9]\d*)$',
        IconRetrieveView.as_view(),
        name='icon-retrieve'),
    re_path(
        r'^icons/update/(?P<id>[1-9]\d*)$',
        IconUpdateView.as_view(),
        name='icon-update'),
    re_path(r'^icons$', IconListView.as_view(), name='icons-list'),
    re_path(
        r'^icons/(?P<id>[1-9]\d*)/approve$',
        IconApproveView.as_view(),
        name='icon-approve'),
    re_path(
        r'^audio/(?P<id>[a-z0-9\W_]+)\.mp3$',
        MP3RetrieveView.as_view(),
        name='audio'),
    re_path(
        r'^categories$',
        CategoriesViewSet.as_view({
            'get': 'list',
            'post': 'create'
        }),
        name='word'),
    re_path(
        r'^categories/(?P<id>[1-9]\d*)$',
        CategoriesViewSet.as_view(
            {
                'get': 'retrieve',
                'put': 'update',
                'delete': 'delete'
            }),
        name='word'),
]
