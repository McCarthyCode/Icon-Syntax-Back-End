from rest_framework import status, generics
from rest_framework.response import Response

from ..models import MP3


class MP3RetrieveView(generics.RetrieveAPIView):
    """
    Generic API View class defining a GET route for retrieving MP3 data.
    """
    name = 'MP3 Retrieve'

    def get(self, request, id):
        """
        GET route for obtaining an MP3 object, either from local starage or the Merriam-Webster media server.
        """
        return Response(MP3.objects.get_mp3(id).obj, status=status.HTTP_200_OK)
