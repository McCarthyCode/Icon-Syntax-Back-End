from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import exceptions, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..models import Category
from ..serializers import CategorySerializer

from api.authentication.permissions import IsSafeMethod, IsVerified
from api.exceptions import BadRequestError


class CategoriesViewSet(GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSafeMethod | IsVerified | IsAdminUser]

    def list(self, request):
        parent = request.data.get('parent', None)
        if parent: parent = int(parent)

        return Response(
            {
                'data': [
                    x.obj for x in Category.objects.filter(
                        parent=parent).order_by('id')
                ]
            },
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        return Response(
            {'data': get_object_or_404(Category, *args, **kwargs).obj},
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

    def update(self, request, id):
        if request.method != 'PUT':
            raise exceptions.MethodNotAllowed(request.method)

        category = get_object_or_404(Category, id=id)
        serializer = self.serializer_class(data=request.data, instance=category)

        if not serializer.is_valid():
            raise BadRequestError()

        category = serializer.save()

        return Response(category.obj, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        if request.method != 'DELETE':
            raise exceptions.MethodNotAllowed(request.method)

        category = get_object_or_404(Category, id=id)
        for cat in Category.subcategories(category.id):
            cat.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
