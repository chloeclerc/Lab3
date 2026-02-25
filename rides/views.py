from django.shortcuts import render
from django.db.models import Q

from .models import Person
from .forms import RideForm


def index(request):
    context = {}
    form = RideForm(request.GET or None)
    context["form"] = form

    # default: no results until a valid state is provided
    context["people"] = Person.objects.none()

    if form.is_valid():
        city = (form.cleaned_data.get("city") or "").strip()
        state = (form.cleaned_data.get("state") or "").strip()
        only_drivers = form.cleaned_data.get("only_drivers")  # NEW

        # required: filter by 2-letter destination state, case-insensitive
        people = Person.objects.filter(destination_state__iexact=state)

        # optional: if city provided, match origination OR destination city
        if city:
            people = people.filter(
                Q(origination__icontains=city) | Q(destination_city__icontains=city)
            )

        # NEW: if checkbox checked, only show those taking passengers
        if only_drivers:
            people = people.filter(taking_passengers=True)

        context["people"] = people
        context["inputExists"] = True  # keep your template logic happy if it uses this

    return render(request, "index_view.html", context)