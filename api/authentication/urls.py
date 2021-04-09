from django.urls import re_path, include

from .views import *

app_name = 'api.authentication'

urlpatterns = [
    re_path('^register$', RegisterView.as_view(), name='register'),
    re_path('^register/verify$', RegisterVerifyView.as_view(), name='verify'),
    re_path('^login$', LoginView.as_view(), name='login'),
    re_path('^logout$', LogoutView.as_view(), name='logout'),
]
