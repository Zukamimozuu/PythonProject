# context_processors.py
from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-date')  # Correct field to order by
        return {'notifications': notifications}
    return {'notifications': []}
