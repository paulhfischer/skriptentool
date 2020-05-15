from django.core.management import BaseCommand

from core.models import Balance
from core.models import User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("balance", type=float)
        parser.add_argument("user", type=str)

    def handle(self, *args, **options):
        Balance(
            user=User.objects.get(username=options["user"]),
            amount=options["balance"],
            counted=True,
            type=Balance.INITIAL,
        ).save()
