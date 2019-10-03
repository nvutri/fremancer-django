"""View handlers for main page."""
from django.shortcuts import render
from django.template import RequestContext
from fremancer_users.models import UserProfile


def index(request):
    """Main index page."""
    if request.user.is_authenticated():
        profile = UserProfile.objects.get(user=request.user)
        if profile.is_freelancer():
            return render(request, 'freelancer.html')
        elif profile.is_hirer():
            return render(request, 'hirer.html')
    return render(request, 'anonymous.html')
