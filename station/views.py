from rest_framework import viewsets

from station.models import Bus
from station.serializers import BusSerializer


class BusViewSet(
    viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
