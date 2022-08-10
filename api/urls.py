from django.urls import re_path, include

app_name = 'api'

urlpatterns = [
    re_path(r'^auth/', include('api.authentication.urls', namespace='auth')),
    re_path(r'^', include('api.dictionary.urls', namespace='dict')),
    re_path(r'^', include('api.pdf.urls', namespace='pdf')),
    re_path(r'^blog/', include('api.blog.urls', namespace='blog')),
]
