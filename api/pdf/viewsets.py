from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.authentication.permissions import IsAdminOrReadOnly

from .models import PDF
from .serializers import *


class PDFViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing PDFs.
    """
    queryset = PDF.objects.all()
    serializer_class = PDFSerializer
    permission_classes = [IsAdminOrReadOnly]

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        obj = {'success': 'PDF upload successful.', 'data': res.data}

        return Response(obj, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        objs = PDF.objects.all()

        if 'categories' in request.query_params:
            categories = request.query_params.get('categories', '').split(',')
            objs = PDF.objects.filter(
                categories__id__in=set(map(int, categories)))

        if 'page' in request.query_params:
            objs = objs[:100]  # TODO add pagination

        objs = list(map(lambda x: x.obj, objs))

        count = len(objs)
        obj = {
            'success':
            f'Found {count} PDF{"" if count == 1 else "s"} that match{"es" if count == 1 else ""} the given query.',
            'data': objs
        }

        return Response(obj)

    def retrieve(self, request, *args, **kwargs):
        res = super().retrieve(request, *args, **kwargs)
        obj = {'success': 'PDF retrieved successfully.', 'data': res.data}

        return Response(obj)


class PDFCategoryViewset(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing PDFs.
    """
    queryset = PDF.Category.objects.all()
    serializer_class = PDFCategorySerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        obj = {
            'success': 'PDF category created successfully.',
            'data': res.data
        }

        return Response(obj, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        objs = PDF.Category.objects.all()

        if 'page' in request.query_params:
            objs = objs[:100]  # TODO: add pagination

        objs = list(map(lambda x: x.obj, objs))

        count = len(objs)
        obj = {
            'success':
            f'Found {count} categor{"y" if count == 1 else "ies"} that match{"es" if count == 1 else ""} the given query.',
            'data': objs
        }

        return Response(obj, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)
        obj = {'success': 'PDF Category update successful.', 'data': res.data}

        return Response(obj, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
