from django.urls import re_path, include

from .views import *

app_name = 'api.authentication'

urlpatterns = [
    re_path(r'^register/', RegisterView.as_view(), name='register'),
    re_path(r'^verify/', VerifyView.as_view(), name='verify'),
    re_path(r'^login/', LoginView.as_view(), name='login'),
]
