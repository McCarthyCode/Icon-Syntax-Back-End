import copy
import json

from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse

from rest_framework import permissions, viewsets, status
from rest_framework.response import Response

from ..serializers import SubscriptionSerializer
from ..models import Subscription


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Subscription.objects.all()

    def list(self, request, ext=None):
        if ext not in {None, 'json', 'csv', 'txt'}:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            Subscription.objects.all(), many=True)

        detail = request.query_params.get(
            'detail', 'true' if ext == 'csv' else 'false').lower() != 'false'

        if ext in {None, 'json'}:
            data = serializer.data if detail else \
                [x['email'] for x in serializer.data]
            response = HttpResponse(
                json.dumps(data), content_type='application/json')
            if ext:
                response['Content-Disposition'] = \
                    'attachment;filename=subscriptions.json'

            return response
        elif detail:
            data = [','.join(map(str, x.values())) for x in serializer.data]
        else:
            data = [x['email'] for x in serializer.data]

        header = request.query_params.get(
            'header', 'true' if ext == 'csv' else 'false').lower() != 'false'
        if header:
            data = ['id,created,updated,email' if detail else 'email', *data]

        if ext in {'csv', 'txt'}:
            data = '\n'.join([*data, ''])  # join and add trailing newline

        if ext:
            content_type = {
                'csv': 'text/csv',
                'txt': 'text/plain'
            }
            response = HttpResponse(data, content_type=content_type[ext])
            response['Content-Disposition'] = \
                f'attachment;filename=subscriptions.{ext}'

            return response

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def lookup(self, request):
        detail = request.query_params.get('detail', 'false').lower() != 'false'
        subscription = get_object_or_404(
            Subscription, email=request.query_params.get('email'))

        serializer = self.serializer_class(subscription)

        return Response(serializer.data if detail else subscription.pk)
