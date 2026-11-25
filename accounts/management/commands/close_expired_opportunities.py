from django.core.management.base import BaseCommand

from accounts.services import close_expired_opportunities


class Command(BaseCommand):
    help = "Close published opportunities whose deadlines have passed."

    def handle(self, *args, **options):
        count = close_expired_opportunities()
        self.stdout.write(f"Closed {count} expired opportunities.")
