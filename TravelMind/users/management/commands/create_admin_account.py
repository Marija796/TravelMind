"""
Ensures a working Administrator account exists, so a fresh clone/deploy of
this project has a real, reproducible way to reach the Admin Dashboard
instead of relying on someone having created one by hand through the shell.

Idempotent: if the account already exists, it is left untouched (including
its password) - this only ever creates, never resets credentials on an
account that might have since been changed by a real person.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

ADMIN_USERNAME = 'admin_test'
ADMIN_EMAIL = 'admin@travelmind.com'
ADMIN_PASSWORD = 'AdminPass123!'


class Command(BaseCommand):
    help = 'Create the default TravelMind Administrator test account (idempotent - safe to run on every deploy).'

    def handle(self, *args, **options):
        if User.objects.filter(username=ADMIN_USERNAME).exists():
            self.stdout.write(self.style.WARNING(
                f'Administrator account "{ADMIN_USERNAME}" already exists - leaving it untouched.'
            ))
            return

        User.objects.create_user(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            role='admin',
        )
        self.stdout.write(self.style.SUCCESS(
            f'Created Administrator account: username="{ADMIN_USERNAME}" (or email "{ADMIN_EMAIL}") '
            f'password="{ADMIN_PASSWORD}". Log in at /login with either - you will be redirected to '
            '/admin automatically.'
        ))
