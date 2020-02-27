from django.contrib.auth.models import User
from django.core.management import BaseCommand

from core.models import Balance


class Command(BaseCommand):
    help = "Setze Anfangskassenstand"

    def add_arguments(self, parser):
        parser.add_argument("balance", type=float)

    def handle(self, *args, **options):
        Balance(user=User.objects.all()[0], amount=options["balance"], counted=True, type="Ersteinlage").save()
