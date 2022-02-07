from rest_framework import viewsets
from rest_framework.response import Response

from api.authentication.permissions import IsAdminOrReadOnly

from .models import PDF
from .serializers import PDFSerializer


class PDFViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing PDFs.
    """
    queryset = PDF.objects.all()
    serializer_class = PDFSerializer
    permission_classes = [IsAdminOrReadOnly]

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        obj = {'success': 'PDF upload successful.', 'data': res.data}

        return Response(obj)

    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        count = len(res.data)
        obj = {
            'success':
            f'Found {count} PDF{"" if count == 1 else "s"} that match{"es" if count == 1 else ""} the given query.',
            'data': res.data
        }

        return Response(obj)

    def retrieve(self, request, *args, **kwargs):
        res = super().retrieve(request, *args, **kwargs)
        obj = {'success': 'PDF retrieved successfully.', 'data': res.data}

        return Response(obj)
