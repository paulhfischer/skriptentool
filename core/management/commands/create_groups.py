from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Erstelle Gruppen mit entsprechenden Rechten"

    def handle(self, *args, **options):
        print("Erstelle Finanzer")
        finanzer, created = Group.objects.get_or_create(name="Finanzer")
        finanzer.permissions.add(Permission.objects.get(name="Can view Kaution"))
        finanzer.permissions.add(Permission.objects.get(name="Can view Kautionsschein"))
        finanzer.permissions.add(Permission.objects.get(name="Can view Skript"))
        finanzer.permissions.add(Permission.objects.get(name="Can view Druckkontingent"))
        finanzer.permissions.add(Permission.objects.get(name="Can view Verkaufsschicht"))
        finanzer.permissions.add(Permission.objects.get(name="Can change Verkaufsschicht"))
        print("Erstelle Referent")
        referent, created = Group.objects.get_or_create(name="Referent")
        referent.permissions.add(Permission.objects.get(name="Can view Autor"))
        referent.permissions.add(Permission.objects.get(name="Can change Autor"))
        referent.permissions.add(Permission.objects.get(name="Can add Autor"))
        referent.permissions.add(Permission.objects.get(name="Can delete Autor"))
        referent.permissions.add(Permission.objects.get(name="Can view Kaution"))
        referent.permissions.add(Permission.objects.get(name="Can change Kaution"))
        referent.permissions.add(Permission.objects.get(name="Can add Kaution"))
        referent.permissions.add(Permission.objects.get(name="Can delete Kaution"))
        referent.permissions.add(Permission.objects.get(name="Can view Kautionsschein"))
        referent.permissions.add(Permission.objects.get(name="Can change Kautionsschein"))
        referent.permissions.add(Permission.objects.get(name="Can view Skript"))
        referent.permissions.add(Permission.objects.get(name="Can change Skript"))
        referent.permissions.add(Permission.objects.get(name="Can add Skript"))
        referent.permissions.add(Permission.objects.get(name="Can delete Skript"))
        referent.permissions.add(Permission.objects.get(name="Can view Druckkontingent"))
        referent.permissions.add(Permission.objects.get(name="Can change Druckkontingent"))
        referent.permissions.add(Permission.objects.get(name="Can add Druckkontingent"))
        referent.permissions.add(Permission.objects.get(name="Can delete Druckkontingent"))
        referent.permissions.add(Permission.objects.get(name="Can view Verkaufsschicht"))
        referent.permissions.add(Permission.objects.get(name="Can change Verkaufsschicht"))
        referent.permissions.add(Permission.objects.get(name="Can delete Verkaufsschicht"))
        print("Erstelle Verkäufer")
        Group.objects.get_or_create(name="Verkäufer")
