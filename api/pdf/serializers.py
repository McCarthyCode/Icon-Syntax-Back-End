from collections import OrderedDict

from rest_framework import serializers
from api.pdf.models import PDF


class PDFSerializer(serializers.ModelSerializer):
    pdf = serializers.FileField()

    class Meta:
        model = PDF
        fields = ['id', 'topic', 'title', 'pdf', 'md5']
        read_only_fields = ['id', 'md5']

    @property
    def data(self):
        return OrderedDict(
            {
                'id': self.instance.id,
                'topic': self.instance.topic,
                'title': self.instance.title,
                'pdf': self.instance.pdf.name,
                'md5': self.instance.md5
            })
