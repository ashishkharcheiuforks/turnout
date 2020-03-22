from django.http import Http404
from django.utils.timezone import now
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.analytics import statsd

from .models import StorageItem
from .serializers import StorageTokenSerializer


class DownloadView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StorageTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            item = StorageItem.objects.get(token=serializer.validated_data["token"])
        except StorageItem.DoesNotExist:
            statsd.increment("turnout.storage.download_failure_missing")
            raise Http404

        if item.expires < now():
            return Response(
                {"detail": "Token expired. Please request a new token."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response({"url": item.file.url})


class ResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StorageTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            item = StorageItem.objects.get(token=serializer.validated_data["token"],)
        except StorageItem.DoesNotExist:
            statsd.increment("turnout.storage.reset_failure_missing")
            raise Http404

        item.refresh_token()
        # TODO: Trigger email to user with new token

        return Response(status=status.HTTP_201_CREATED)
