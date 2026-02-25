from django import forms


class RideForm(forms.Form):
    city = forms.CharField(label="City", max_length=64, required=False)
    state = forms.CharField(label="State (2 letters)", max_length=2, required=True)

    # NEW
    only_drivers = forms.BooleanField(
        label="Only show rides accepting passengers",
        required=False,
        initial=False,
    )

    def clean_state(self):
        state = (self.cleaned_data.get("state") or "").strip()
        if len(state) != 2:
            raise forms.ValidationError("State must be exactly 2 letters (e.g., NJ).")
        return state