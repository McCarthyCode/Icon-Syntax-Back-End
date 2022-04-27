from rest_framework import permissions, viewsets
from rest_framework.response import Response

from ..serializers import SubscriptionSerializer
from ..models import Subscription


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Subscription.objects.all()

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)

        return Response(list(map(lambda x: x['email'], serializer.data)))
