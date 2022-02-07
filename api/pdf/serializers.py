from collections import OrderedDict

from rest_framework import serializers
from api.pdf.models import PDF


class PDFSerializer(serializers.ModelSerializer):
    pdf = serializers.FileField()

    class Meta:
        model = PDF
        fields = ['id', 'pdf', 'title', 'topic', 'md5']
        read_only_fields = ['id', 'pdf', 'md5']

    @property
    def data(self):
        return OrderedDict(
            {
                'id': self.instance.id,
                'title': self.instance.title,
                'pdf': self.instance.pdf.name,
                'topic': self.instance.topic,
            })
