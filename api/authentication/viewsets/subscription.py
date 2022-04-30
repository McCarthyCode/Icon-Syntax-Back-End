import copy
import json

from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse

from rest_framework import permissions, viewsets
from rest_framework.response import Response

from ..serializers import SubscriptionSerializer
from ..models import Subscription


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Subscription.objects.all()

    def list(self, request, ext='json'):
        serializer = self.serializer_class(
            Subscription.objects.all(), many=True)

        detail = request.query_params.get(
            'detail', 'true' if ext == 'csv' else 'false').lower() != 'false'

        if ext == 'json':
            data = serializer.data if detail else [
                x['email'] for x in serializer.data
            ]

            return Response(data)
        elif detail:
            data = [','.join(map(str, x.values())) for x in serializer.data]
        else:
            data = [x['email'] for x in serializer.data]

        header = request.query_params.get(
            'header', 'true' if ext == 'csv' else 'false').lower() != 'false'
        if header:
            data = ['id,created,updated,email' if detail else 'email', *data]

        data = '\n'.join([*data, ''])
        content_type = {'csv': 'text/csv', 'txt': 'text/plain'}

        return HttpResponse(data, content_type=content_type[ext])

    # def create(self, request, ext=None):
    #     if ext:
    #         return Response(status=405)

    #     breakpoint()

    #     return super().create(self, request)

    # def retrieve(self, request, pk=None):
    #     return Response(get_object_or_404(Subscription, pk=pk).obj)

    # def update(self, request, old_email=None, new_email=None):
    #     instance = get_object_or_404(Subscription, email=old_email)
    #     # created = copy.deepcopy(instance.created)
    #     # print(1, created)

    #     serializer = self.serializer_class(
    #         instance,
    #         data={
    #             'email': new_email,
    #             # 'created': created
    #         },
    #         partial=True)

    #     serializer.is_valid(raise_exception=True)
    #     # updated_instance = serializer.update(
    #     #     instance, serializer.validated_data)

    #     # instance.delete()

    #     # updated_instance.created = created
    #     # updated_instance.save()
    #     # serializer.save()

    #     instance = serializer.update(instance, serializer.validated_data)

    #     # instance.delete()

    #     # updated_instance.created = created
    #     # updated_instance.save()
    #     print(2, serializer.validated_data)

    #     # serializer.save()
    #     # instance, bool_created = Subscription.objects.update()
    #     # email=old_email, email=new_email)

    #     # print(3, instance.created)
    #     # print(4, serializer.data['created'])

    #     return Response(serializer.data)

    # def partial_update(self, request, old_email=None, new_email=None):
    #     return self.update(request, old_email, new_email)
