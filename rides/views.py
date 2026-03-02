import logging
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count, Q
from django.urls import reverse

from .models import Person, Profile, Ride, RidePassenger
from .forms import ProfileCreateForm, ProfileEditForm, RideCreateForm, RideEditForm, RideForm

logger = logging.getLogger(__name__)
SESSION_PROFILE_ID = "handyrides_profile_id"


def _get_profile_from_session(request):
    """Return the Profile for the current session, or None."""
    pid = request.session.get(SESSION_PROFILE_ID)
    if not pid:
        return None
    return Profile.objects.filter(id=pid).first()


def index(request):
    context = {}
    form = RideForm(request.GET or None)
    context["form"] = form
    context["rides"] = Ride.objects.none()
    context["search_error"] = None

    if form.is_valid():
        try:
            city = (form.cleaned_data.get("city") or "").strip()
            state = (form.cleaned_data.get("state") or "").strip()
            only_drivers = form.cleaned_data.get("only_drivers")

            rides = (
                Ride.objects.filter(destination_state__iexact=state)
                .annotate(passenger_count=Count("passengers"))
            )
            if city:
                rides = rides.filter(
                    Q(origin_city__icontains=city) | Q(destination_city__icontains=city)
                )
            if only_drivers:
                rides = rides.filter(taking_passengers=True)
            rides = rides.select_related("driver_profile").order_by("date", "time")

            profile = _get_profile_from_session(request)
            for ride in rides:
                pc = ride.passenger_count
                if ride.estimated_total_cost is not None:
                    ride.cost_per_person = ride.estimated_total_cost / (1 + pc)
                else:
                    ride.cost_per_person = None
                ride.seats_left = max(0, ride.seats_available - pc)
                ride.already_joined = (
                    profile is not None
                    and RidePassenger.objects.filter(ride=ride, profile=profile).exists()
                )
                ride.is_driver = (
                    profile is not None
                    and ride.driver_profile_id is not None
                    and profile.id == ride.driver_profile_id
                )
                ride.can_join = (
                    ride.taking_passengers
                    and ride.seats_left > 0
                    and profile is not None
                    and not ride.is_driver
                    and not ride.already_joined
                )
                ride.can_click_join = (
                    ride.taking_passengers
                    and ride.seats_left > 0
                    and not ride.already_joined
                    and not ride.is_driver
                )

            context["rides"] = rides
            context["inputExists"] = True
        except Exception as e:
            logger.exception("Search failed: %s", e)
            context["search_error"] = str(e)
            context["inputExists"] = True

    return render(request, "index_view.html", context)


def create_profile(request):
    profile = _get_profile_from_session(request)
    if profile:
        return redirect("rides:profile_view")
    form = ProfileCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        profile = form.save()
        request.session[SESSION_PROFILE_ID] = profile.id
        request.session.modified = True
        return redirect("rides:profile_view")
    return render(request, "create_profile.html", {"form": form})


def profile_view(request):
    profile = _get_profile_from_session(request)
    if not profile:
        return redirect("rides:create_profile")
    return render(request, "profile_view.html", {"profile": profile})


def profile_edit(request):
    profile = _get_profile_from_session(request)
    if not profile:
        return redirect("rides:create_profile")
    form = ProfileEditForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("rides:profile_view")
    return render(request, "profile_edit.html", {"form": form, "profile": profile})


def profile_lookup(request):
    """
    Recover profile access by email when session is lost.
    If email matches a profile, set session and redirect to profile_view.
    """
    profile = _get_profile_from_session(request)
    if profile:
        return redirect("rides:profile_view")

    error = None
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        if email:
            profile = Profile.objects.filter(email__iexact=email).first()
            if profile:
                request.session[SESSION_PROFILE_ID] = profile.id
                request.session.modified = True
                return redirect("rides:profile_view")
            error = "No profile found with that email."
        else:
            error = "Please enter your email."

    return render(request, "profile_lookup.html", {"error": error})


def create_ride(request):
    profile = _get_profile_from_session(request)
    if not profile:
        return redirect("rides:create_profile")
    form = RideCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ride = form.save(commit=False)
        ride.driver_profile = profile
        ride.save()
        return redirect("rides:create_ride_success")
    return render(request, "create_ride.html", {"form": form, "saved": False, "profile": profile})


def create_ride_success(request):
    profile = _get_profile_from_session(request)
    if not profile:
        return redirect("rides:create_profile")
    form = RideCreateForm()
    return render(request, "create_ride.html", {"form": form, "saved": True, "profile": profile})


def join_ride(request, ride_id):
    profile = _get_profile_from_session(request)
    if not profile:
        return redirect("rides:create_profile")

    ride = get_object_or_404(Ride, id=ride_id)

    if not ride.taking_passengers:
        return redirect("rides:index")
    passenger_count = RidePassenger.objects.filter(ride=ride).count()
    if passenger_count >= ride.seats_available:
        return redirect("rides:index")
    if profile == ride.driver_profile:
        return redirect("rides:index")
    if RidePassenger.objects.filter(ride=ride, profile=profile).exists():
        return redirect("rides:index")

    RidePassenger.objects.create(ride=ride, profile=profile)
    query = request.GET.urlencode()
    index_url = reverse("rides:index")
    if query:
        return redirect(f"{index_url}?{query}")
    return redirect(index_url)


def ride_edit(request, ride_id):
    """Edit a ride; only the driver can edit."""
    profile = _get_profile_from_session(request)
    if not profile:
        return redirect("rides:create_profile")

    ride = get_object_or_404(Ride, id=ride_id)
    if ride.driver_profile_id != profile.id:
        return redirect("rides:index")

    form = RideEditForm(request.POST or None, instance=ride)
    if request.method == "POST" and form.is_valid():
        form.save()
        query = request.GET.urlencode()
        index_url = reverse("rides:index")
        if query:
            return redirect(f"{index_url}?{query}")
        return redirect("rides:index")

    return render(request, "ride_edit.html", {"form": form, "ride": ride})


def unjoin_ride(request, ride_id):
    """Remove the current profile from a ride they have joined."""
    profile = _get_profile_from_session(request)
    if not profile:
        return redirect("rides:create_profile")

    ride = get_object_or_404(Ride, id=ride_id)
    rp = RidePassenger.objects.filter(ride=ride, profile=profile).first()
    if rp:
        rp.delete()

    query = request.GET.urlencode()
    index_url = reverse("rides:index")
    if query:
        return redirect(f"{index_url}?{query}")
    return redirect(index_url)
