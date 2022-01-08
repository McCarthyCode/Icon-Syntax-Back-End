from rest_framework import serializers
from api.pdf.models import PDF


class PDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDF
        fields = ['id', 'pdf', 'md5']
        read_only_fields = ['id', 'md5']
