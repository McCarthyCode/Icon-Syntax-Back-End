from django.urls import re_path, include

app_name = 'api'

urlpatterns = [
    re_path(r'^auth/', include('api.authentication.urls', namespace='auth')),
]
