from rest_framework import serializers

from common.utils.fields import SmallUUIDField


class StorageTokenSerializer(serializers.Serializer):
    token = SmallUUIDField()
