from django.urls import re_path, include
from rest_framework.routers import SimpleRouter

from .views import *
from .viewsets import *

app_name = 'api.authentication'

urlpatterns = [
    re_path('^register$', RegisterView.as_view(), name='register'),
    re_path(
        '^register/verify$',
        RegisterVerifyView.as_view(),
        name='register-verify'),
    re_path('^login$', LoginView.as_view(), name='login'),
    re_path('^logout$', LogoutView.as_view(), name='logout'),
    re_path(
        '^password/reset$', PasswordResetView.as_view(), name='password-reset'),
    re_path(
        '^password/forgot$',
        PasswordForgotView.as_view(),
        name='password-forgot'),
    re_path(
        '^password/forgot/verify$',
        PasswordForgotVerifyView.as_view(),
        name='password-forgot-verify'),
    re_path('^refresh$', RefreshView.as_view(), name='refresh'),
]

router = SimpleRouter(trailing_slash=False)
router.register(r'^subscription', SubscriptionViewSet)

urlpatterns += router.urls
