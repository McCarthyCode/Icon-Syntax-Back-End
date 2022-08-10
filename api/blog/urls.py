from rest_framework.routers import SimpleRouter
from .viewsets import *

app_name = 'api.blog'

router = SimpleRouter(trailing_slash=False)

router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = router.urls
