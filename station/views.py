from django.db.models import Count, F
from rest_framework import viewsets

from station.models import Bus, Trip, Facility, Order
from station.serializers import (BusSerializer,
                                 TripSerializer,
                                 TripListSerializer,
                                 BusListSerializer,
                                 FacilitySerializer,
                                 BusRetrieveSerializer,
                                 TripRetriveSerializer, OrderSerializer, OrderListSerializer)


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer


class BusViewSet(
    viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusListSerializer

    @staticmethod
    def _params_to_ints(query_string):
        return [int(str_id) for str_id in query_string.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return BusListSerializer
        elif self.action == "retrieve":
            return BusRetrieveSerializer
        return BusSerializer

    def get_queryset(self):
        queryset = self.queryset

        facilities = self.request.query_params.get("facilities")

        if facilities:
            facilities = self._params_to_ints(facilities)
            queryset = queryset.filter(facilities__id__in=facilities)

        if self.action in ("list", "retrieve"):
            return queryset.prefetch_related("facilities")

        return queryset.distinct()


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
        if self.action == "list":
            queryset = (
                queryset
                .select_related()
                .annotate(tickets_available=F("bus__num_seats") - Count("tickets_taken"))
            )
        elif self.action == "retrieve":
            queryset = queryset.select_related()

        return queryset.order_by("id")


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__trip__bus")

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "list":
            serializer = OrderListSerializer
        return serializer
