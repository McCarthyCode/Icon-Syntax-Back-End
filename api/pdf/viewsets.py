from rest_framework import viewsets
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
