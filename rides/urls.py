from django.urls import path

from . import views

app_name = 'rides'
urlpatterns = [
    path("", views.index, name="index"),
    path("ride/<int:ride_id>/join/", views.join_ride, name="join_ride"),
    path("ride/<int:ride_id>/edit/", views.ride_edit, name="ride_edit"),
    path("ride/<int:ride_id>/unjoin/", views.unjoin_ride, name="unjoin_ride"),
    path("create-profile/", views.create_profile, name="create_profile"),
    path("profile/", views.profile_view, name="profile_view"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/lookup/", views.profile_lookup, name="profile_lookup"),
    path("create-ride/", views.create_ride, name="create_ride"),
    path("create-ride/success/", views.create_ride_success, name="create_ride_success"),
]
