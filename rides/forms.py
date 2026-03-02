from django import forms
from .models import Profile, Ride


class RideForm(forms.Form):
    city = forms.CharField(label="City", max_length=64, required=False)
    state = forms.CharField(label="State (2 letters)", max_length=2, required=True)
    only_drivers = forms.BooleanField(
        label="Only show rides accepting passengers",
        required=False,
        initial=False,
    )

    def clean_state(self):
        state = (self.cleaned_data.get("state") or "").strip()
        if len(state) != 2:
            raise forms.ValidationError("State must be exactly 2 letters (e.g., NJ).")
        return state.upper()


class ProfileCreateForm(forms.ModelForm):
    """is_verified is set automatically from @princeton.edu in Profile.save()."""
    class Meta:
        model = Profile
        exclude = ["user", "is_verified"]
        widgets = {
            "email": forms.EmailInput(attrs={"size": 40}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "quiet_ride_preference": "Prefer quiet ride",
            "music_ok_preference": "Music OK",
        }

    def clean_home_state(self):
        state = (self.cleaned_data.get("home_state") or "").strip()
        if state and len(state) != 2:
            raise forms.ValidationError("Home state must be exactly 2 letters (e.g., NJ).")
        return state.upper() if state else ""


class ProfileEditForm(forms.ModelForm):
    """Same as create; is_verified is auto-set from email."""
    class Meta:
        model = Profile
        exclude = ["user", "is_verified"]
        widgets = {
            "email": forms.EmailInput(attrs={"size": 40}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "quiet_ride_preference": "Prefer quiet ride",
            "music_ok_preference": "Music OK",
        }

    def clean_home_state(self):
        state = (self.cleaned_data.get("home_state") or "").strip()
        if state and len(state) != 2:
            raise forms.ValidationError("Home state must be exactly 2 letters (e.g., NJ).")
        return state.upper() if state else ""


class RideCreateForm(forms.ModelForm):
    """driver_profile is set automatically from session in the view."""
    class Meta:
        model = Ride
        fields = [
            "ride_type",
            "origin_city",
            "origin_state",
            "destination_city",
            "destination_state",
            "date",
            "time",
            "taking_passengers",
            "seats_available",
            "estimated_total_cost",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "origin_city": "Origin city",
            "origin_state": "Origin state (2 letters)",
            "destination_city": "Destination city",
            "destination_state": "Destination state (2 letters)",
            "estimated_total_cost": "Estimated total cost (optional)",
        }

    def clean_origin_state(self):
        state = (self.cleaned_data.get("origin_state") or "").strip()
        if len(state) != 2:
            raise forms.ValidationError("Origin state must be exactly 2 letters.")
        return state.upper()

    def clean_destination_state(self):
        state = (self.cleaned_data.get("destination_state") or "").strip()
        if len(state) != 2:
            raise forms.ValidationError("Destination state must be exactly 2 letters.")
        return state.upper()

    def clean(self):
        data = super().clean()
        if data.get("taking_passengers") is False:
            data["seats_available"] = 0
        return data


class RideEditForm(forms.ModelForm):
    """Same fields as create; driver_profile is not editable (stays as creator)."""
    class Meta:
        model = Ride
        fields = [
            "ride_type",
            "origin_city",
            "origin_state",
            "destination_city",
            "destination_state",
            "date",
            "time",
            "taking_passengers",
            "seats_available",
            "estimated_total_cost",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "ride_type": "Ride type",
            "origin_city": "Origin city",
            "origin_state": "Origin state (2 letters)",
            "destination_city": "Destination city",
            "destination_state": "Destination state (2 letters)",
            "estimated_total_cost": "Estimated total cost (optional)",
        }

    def clean_origin_state(self):
        state = (self.cleaned_data.get("origin_state") or "").strip()
        if len(state) != 2:
            raise forms.ValidationError("Origin state must be exactly 2 letters.")
        return state.upper()

    def clean_destination_state(self):
        state = (self.cleaned_data.get("destination_state") or "").strip()
        if len(state) != 2:
            raise forms.ValidationError("Destination state must be exactly 2 letters.")
        return state.upper()

    def clean(self):
        data = super().clean()
        if data.get("taking_passengers") is False:
            data["seats_available"] = 0
        return data
