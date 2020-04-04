from django.core.management import BaseCommand

from core.models import User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("email", type=str)
        parser.add_argument("first_name", type=str)
        parser.add_argument("last_name", type=str)
        parser.add_argument("password", type=str)

    def handle(self, *args, **options):
        User.objects.create_superuser(
            options["username"],
            options["email"],
            options["first_name"],
            options["last_name"],
            options["password"],
        )
