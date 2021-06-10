from django.urls import re_path, include

from .views import *

app_name = 'api.dictionary'

urlpatterns = [
    re_path(
        r'^(?P<word>[a-zA-Z0-9@:%._+~#]{1,256})$',
        WordView.as_view(),
        name='word'),
    re_path(
        r'^search/(?P<word>[a-zA-Z0-9@:%._+~#]{1,256})$',
        WordSearchView.as_view(),
        name='search'),
    re_path(
        r'^icon/upload$',
        IconUploadView.as_view(),
        name='icon-upload'),
    re_path(
        r'^icon/(?P<id>[1-9]\d*)/approve$',
        IconApproveView.as_view(),
        name='icon-approve'),
]
