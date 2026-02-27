# Profile: person-level only; Ride: driver posting only (no passenger constraints)

import django.db.models.deletion
from django.db import migrations, models


def profile_data_forward(apps, schema_editor):
    """Copy quiet_ride -> quiet_ride_preference, music_ok -> music_ok_preference before dropping."""
    Profile = apps.get_model("rides", "Profile")
    for p in Profile.objects.all():
        p.quiet_ride_preference = getattr(p, "quiet_ride", False)
        p.music_ok_preference = getattr(p, "music_ok", True)
        p.save(update_fields=["quiet_ride_preference", "music_ok_preference"])


def profile_data_backward(apps, schema_editor):
    Profile = apps.get_model("rides", "Profile")
    for p in Profile.objects.all():
        p.quiet_ride = p.quiet_ride_preference
        p.music_ok = p.music_ok_preference
        p.save(update_fields=["quiet_ride", "music_ok"])


class Migration(migrations.Migration):

    dependencies = [
        ("rides", "0002_add_profile_and_ride"),
    ]

    operations = [
        # --- Profile: add new fields ---
        migrations.AddField(
            model_name="profile",
            name="home_city",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="profile",
            name="home_state",
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AddField(
            model_name="profile",
            name="quiet_ride_preference",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="profile",
            name="music_ok_preference",
            field=models.BooleanField(default=True),
        ),
        # Copy data then remove old preference fields
        migrations.RunPython(profile_data_forward, profile_data_backward),
        migrations.RemoveField(model_name="profile", name="quiet_ride"),
        migrations.RemoveField(model_name="profile", name="music_ok"),
        # Remove passenger-specific / non-profile fields
        migrations.RemoveField(model_name="profile", name="preferred_pickup_spot"),
        migrations.RemoveField(model_name="profile", name="pickup_radius_miles"),
        migrations.RemoveField(model_name="profile", name="max_detour_minutes"),
        migrations.RemoveField(model_name="profile", name="origination_state"),
        migrations.AlterField(
            model_name="profile",
            name="vehicle_type",
            field=models.CharField(
                blank=True,
                choices=[("Sedan", "Sedan"), ("SUV", "SUV"), ("Van", "Van"), ("Other", "Other")],
                max_length=16,
            ),
        ),
        # --- Ride: rename and add origin_state ---
        migrations.RenameField(
            model_name="ride",
            old_name="profile",
            new_name="driver_profile",
        ),
        migrations.RenameField(
            model_name="ride",
            old_name="origination",
            new_name="origin_city",
        ),
        migrations.AddField(
            model_name="ride",
            name="origin_state",
            field=models.CharField(default="XX", max_length=2),
        ),
        # Remove passenger-constraint and per-ride preference fields from Ride
        migrations.RemoveField(model_name="ride", name="max_detour_minutes"),
        migrations.RemoveField(model_name="ride", name="pickup_radius_miles"),
        migrations.RemoveField(model_name="ride", name="preferred_pickup_spot"),
        migrations.RemoveField(model_name="ride", name="quiet_ride"),
        migrations.RemoveField(model_name="ride", name="music_ok"),
    ]
