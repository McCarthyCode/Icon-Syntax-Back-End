from django.urls import re_path, include

app_name = 'api'

urlpatterns = [
    re_path('^auth/', include('api.authentication.urls', namespace='auth')),
    re_path('^', include('api.dictionary.urls', namespace='dict')),
]
