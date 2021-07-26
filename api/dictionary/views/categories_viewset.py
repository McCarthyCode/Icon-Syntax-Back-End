from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from ..models import Category


class CategoriesViewSet(GenericViewSet):
    queryset = Category.objects.all()

    def list(self, request):
        return Response(
            {'results': [x.obj for x in Category.objects.filter(parent=None)]},
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, id=None):
        return Response(
            get_object_or_404(Category, id=id).obj,
            status=status.HTTP_200_OK,
        )
