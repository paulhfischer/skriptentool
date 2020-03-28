from django.core.management import BaseCommand

from core.models import Balance, User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("balance", type=float)

    def handle(self, *args, **options):
        # add balance with first user created (if setup.sh is used: superuser)
        Balance(user=User.objects.all()[0], amount=options["balance"], counted=True, type="Ersteinlage").save()
