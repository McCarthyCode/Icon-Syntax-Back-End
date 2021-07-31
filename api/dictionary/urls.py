import string
from django.urls import re_path, include
from .views import *

app_name = 'api.dictionary'

urlpatterns = [
    # re_path(
    #     r'^search/(?P<word>[a-zA-Z0-9@:%._+~#]{1,80})$',
    #     IconSearchView.as_view(),
    #     name='search'),
    re_path(r'^icons/upload$', IconUploadView.as_view(), name='icon-upload'),
    re_path(
        r'^icons/(?P<id>[1-9]\d*)$',
        IconRetrieveView.as_view(),
        name='icon-retrieve'),
    re_path(r'^icons$', IconListView.as_view(), name='icons-list'),
    re_path(
        r'^icons/(?P<id>[1-9]\d*)/approve$',
        IconApproveView.as_view(),
        name='icon-approve'),
    # re_path(
    #     r'^audio/(?P<id>[a-z0-9\W]+)\.mp3$',
    #     MP3RetrieveView.as_view(),
    #     name='audio'),
    # re_path(
    #     r'^(?P<word>[a-zA-Z0-9@:%._+~#]{1,80})$',
    #     WordView.as_view(),
    #     name='word'),
    re_path(
        r'^categories$',
        CategoriesViewSet.as_view({'get': 'list'}),
        name='word'),
    re_path(
        r'^categories/(?P<id>[1-9]\d*)$',
        CategoriesViewSet.as_view({'get': 'retrieve'}),
        name='word'),
]