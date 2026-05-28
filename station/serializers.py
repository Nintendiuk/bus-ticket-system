from rest_framework import serializers
from station.models import Bus
from typing import Any


class BusSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    info = serializers.CharField(required=False, max_length=255)
    num_seats = serializers.IntegerField(required=True)

    def create(self, validated_data: Any) -> Bus:
        return Bus.objects.create(**validated_data)

    def update(self, instance: Bus, validated_data: Any) -> Bus:
        instance.info = validated_data.get('info', instance.info)
        instance.num_seats = validated_data.get('num_seats', instance.num_seats)
        instance.save()
        return instance
