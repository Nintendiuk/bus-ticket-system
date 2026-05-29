from django.db import models
from django.db.models import UniqueConstraint
from rest_framework.exceptions import ValidationError

from app import settings


class Facility(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "facilities"


    def __str__(self):
        return self.name


class Bus(models.Model):
    info = models.CharField(max_length=255, null=True)
    num_seats = models.IntegerField()
    facilities = models.ManyToManyField(Facility, related_name='buses')

    class Meta:
        verbose_name_plural = "buses"


    @property
    def is_small(self):
        return self.num_seats <= 25

    def __str__(self):
        return f"Bus: {self.info} (id = {self.id})"


class Trip(models.Model):
    source = models.CharField(max_length=63)
    destination = models.CharField(max_length=63)
    departure = models.DateTimeField()
    bus = models.ForeignKey("Bus", on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["source", "destination"]),
            models.Index(fields=["departure"]),
        ]

    def __str__(self):
        return f"Trip: {self.source} to {self.destination}({self.departure})"


class Ticket(models.Model):
    seat = models.IntegerField()
    trip = models.ForeignKey("Trip", on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["seat", "trip"], name="unique_seat_trip")
        ]

    def __str__(self):
        return f"{self.trip} - (seat - {self.seat})"

    def clean(self):
        if self.trip_id:
            if not (1 <= self.seat <= self.trip.bus.num_seats):
                raise ValidationError({
                    "seat": f"seat must be in range [1, {self.trip.bus.num_seats}], not {self.seat}"
                })
        else:
            raise ValidationError({"trip": "A ticket must be associated with a trip."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)
