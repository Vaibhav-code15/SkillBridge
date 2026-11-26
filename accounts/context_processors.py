def unread_notifications(request):
    user = request.user
    if user.is_authenticated and user.role == user.Role.STUDENT and not user.is_superuser:
        return {
            "unread_notification_count": user.notifications.filter(read_at__isnull=True).count()
        }
    return {}
