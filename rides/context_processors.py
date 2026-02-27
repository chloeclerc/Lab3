"""
Context processors for the rides app.
Exposes the current session profile to all templates.
"""

from .models import Profile

SESSION_PROFILE_ID = "handyrides_profile_id"


def profile(request):
    """
    Add the current session profile to template context.
    Returns {'profile': Profile or None} so templates can conditionally
    show "My profile" vs "Create profile".
    """
    pid = request.session.get(SESSION_PROFILE_ID)
    if not pid:
        return {"profile": None}
    profile_obj = Profile.objects.filter(id=pid).first()
    return {"profile": profile_obj}
