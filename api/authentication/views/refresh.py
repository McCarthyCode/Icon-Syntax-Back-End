from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.authentication import NON_FIELD_ERRORS_KEY

from ..serializers import RefreshSerializer


class RefreshView(GenericAPIView):
    """
    View to take a refresh token when an access token is expired and obtain new credentials.
    """
    serializer_class = RefreshSerializer

    def initial(self, request, *args, **kwargs):
        """
        This method overrides the default APIView method so exceptions can be handled.
        """
        try:
            super().initial(request, *args, **kwargs)
        except (InvalidToken, AuthenticationFailed, NotAuthenticated) as exc:
            detail = exc.detail['detail'] \
                if 'detail' in exc.detail else exc.detail

            # Append a period because punctuation errors are annoying.
            if detail[-1] not in '.?!':
                detail = ErrorDetail(str(detail) + '.', detail.code)

            raise AuthenticationFailed(
                {NON_FIELD_ERRORS_KEY: [detail]}, detail.code)

    def post(self, request):
        """
        POST method for refreshing an access token
        """
        redirect_uri = request.query_params.get('redirect', '/')
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as exc:
            return Response(
                {NON_FIELD_ERRORS_KEY: [exc.detail]}, exc.status_code)

        return Response(
            {
                'success': str(_('You have successfully refreshed.')),
                'redirect': redirect_uri,
                'credentials': serializer.validated_data
            },
            status=status.HTTP_303_SEE_OTHER)
