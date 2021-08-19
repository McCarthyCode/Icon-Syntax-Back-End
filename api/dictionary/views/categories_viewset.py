from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import exceptions, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from ..models import Category
from ..serializers import CategorySerializer

from api.exceptions import BadRequestError


class CategoriesViewSet(GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request):
        return Response(
            {
                'results': [
                    x.obj for x in Category.objects.filter(
                        parent=None).order_by('name')
                ]
            },
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, id=None):
        return Response(
            get_object_or_404(Category, id=id).obj,
            status=status.HTTP_200_OK,
        )

    def create(self, request):
        if request.method != 'POST':
            raise exceptions.MethodNotAllowed(request.method)

        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            raise BadRequestError()

        category = serializer.save()

        return Response(category.obj, status=status.HTTP_201_CREATED)
