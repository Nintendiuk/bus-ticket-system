from rest_framework import viewsets

from station.models import Bus, Trip, Facility
from station.serializers import (BusSerializer,
                                 TripSerializer,
                                 TripListSerializer,
                                 BusListSerializer,
                                 FacilitySerializer,
                                 BusRetrieveSerializer,
                                 TripRetriveSerializer)


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer


class BusViewSet(
    viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusListSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BusListSerializer
        elif self.action == "retrieve":
            return BusRetrieveSerializer
        return BusSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.prefetch_related("facilities")

        return queryset


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all().select_related()

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        elif self.action == "retrieve":
            return TripRetriveSerializer
        return TripSerializer


    def get_queryset(self):
        queryset = self.queryset
        if self.action == ("list", "retrieve"):
            return queryset.select_related()

        return queryset
