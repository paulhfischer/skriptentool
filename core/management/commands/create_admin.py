from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("password", type=str)

    def handle(self, *args, **options):
        admin = User.objects.create_superuser(options["username"], "", options["password"])
        # add user to all existing groups
        for group in Group.objects.all():
            group.user_set.add(admin)
