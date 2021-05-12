from rest_framework import serializers
from rest_framework.serializers import Serializer


class IOSerializer(Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class MessageSerializer(IOSerializer):
    message = serializers.CharField(required=True)


class IdSerializer(IOSerializer):
    id = serializers.CharField(required=True)
