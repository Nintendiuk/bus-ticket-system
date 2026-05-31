from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from station.models import Bus, Trip, Facility, Ticket, Order


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ("id", "name")


class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ("id", "info", "num_seats", "is_small", "facilities")


class BusImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)

    class Meta:
        model = Bus
        fields = ("id", "image")


class BusListSerializer(BusSerializer):
    facilities = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )


class BusRetrieveSerializer(BusSerializer):
    facilities = FacilitySerializer(many=True)


class TripSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trip
        fields = ("id", "source", "destination", "departure", "bus")


class TripListSerializer(serializers.ModelSerializer):
    bus_info = serializers.CharField(source="bus.info", read_only=True)
    bus_num_seats = serializers.IntegerField(source="bus.num_seats", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trip
        fields = ("id",
                  "source",
                  "destination",
                  "departure",
                  "bus_info",
                  "bus_num_seats",
                  "tickets_available"
                  )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "seat", "trip")

    def validate(self, attrs):
        Ticket.validate_seat(
            attrs["seat"],
            attrs["trip"].bus.num_seats,
            serializers.ValidationError
        )


class TripRetriveSerializer(TripListSerializer):
    bus = BusRetrieveSerializer(many=False, read_only=True)
    taken_seats = (serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="seat",
        source="tickets"
    ))

    class Meta:
        model = Trip
        fields = ("id",
                  "source",
                  "destination",
                  "departure",
                  "bus_info",
                  "bus_num_seats",
                  "taken_seats")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class TicketListSerializer(TicketSerializer):
    trip = TripListSerializer(read_only=True)


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
