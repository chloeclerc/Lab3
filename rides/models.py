from django.conf import settings
from django.db import models


class Person(models.Model):
  first_name = models.CharField(max_length=64)
  origination = models.CharField(max_length=64)
  destination_city = models.CharField(max_length=64)
  destination_state = models.CharField(max_length=2)
  date = models.DateField()
  time = models.TimeField()
  taking_passengers = models.BooleanField(default=False)
  seats_available = models.IntegerField(default=0)


class Profile(models.Model):
  """Person-level, stable info and general preferences (not per-ride). One per User when linked."""
  VEHICLE_TYPE_CHOICES = [
      ("Sedan", "Sedan"),
      ("SUV", "SUV"),
      ("Van", "Van"),
      ("Other", "Other"),
  ]

  user = models.OneToOneField(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name="profile",
      null=True,
      blank=True,
  )
  # Basic info
  first_name = models.CharField(max_length=64)
  last_name = models.CharField(max_length=64, blank=True)
  email = models.EmailField(unique=True)
  home_city = models.CharField(max_length=64, blank=True)
  home_state = models.CharField(max_length=2, blank=True)

  # Preferences
  quiet_ride_preference = models.BooleanField(default=False)
  music_ok_preference = models.BooleanField(default=True)
  notes = models.CharField(max_length=255, blank=True)

  # Driver details (optional; only if this profile is a driver)
  vehicle_type = models.CharField(max_length=16, choices=VEHICLE_TYPE_CHOICES, blank=True)
  # Set from @princeton.edu email on save; not user-editable
  is_verified = models.BooleanField(default=False)

  def __str__(self):
      return f"{self.first_name} {self.last_name}".strip() or self.email

  def save(self, *args, **kwargs):
      email = (self.email or "").strip().lower()
      self.is_verified = email.endswith("@princeton.edu")
      super().save(*args, **kwargs)


class Ride(models.Model):
  """Driver offering a ride: per-ride posting only (no passenger constraints)."""
  driver_profile = models.ForeignKey(
      Profile, on_delete=models.CASCADE, related_name="rides", blank=True, null=True
  )
  origin_city = models.CharField(max_length=64)
  origin_state = models.CharField(max_length=2)
  destination_city = models.CharField(max_length=64)
  destination_state = models.CharField(max_length=2)
  date = models.DateField()
  time = models.TimeField()
  taking_passengers = models.BooleanField(default=False)
  seats_available = models.PositiveIntegerField(default=0)
  estimated_total_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
  notes = models.CharField(max_length=255, blank=True)

  def __str__(self):
      return f"{self.origin_city}, {self.origin_state} → {self.destination_city}, {self.destination_state}"


class RidePassenger(models.Model):
  """Records that a profile has joined a ride (passenger)."""
  ride = models.ForeignKey(
      Ride, on_delete=models.CASCADE, related_name="passengers"
  )
  profile = models.ForeignKey(
      Profile, on_delete=models.CASCADE, related_name="joined_rides"
  )

  class Meta:
      unique_together = [["ride", "profile"]]
