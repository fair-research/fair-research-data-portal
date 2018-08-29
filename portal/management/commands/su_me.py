from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    help = 'Make settings.ME a superuser'
    #
    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '--name', dest='name', required=False,
    #         help='The Name of the user',
    #     )

    def handle(self, *args, **options):
        try:
            u = User.objects.filter(username=settings.ME).first()
            if not u.is_staff or not u.is_superuser:
                u.is_staff = True
                u.is_superuser = True
                u.save()
                print('{} is now a superuser'.format(u))
            else:
                print('{} is already a superuser'.format(u))
        except AttributeError:
            print("Please set username ME = 'person@globusid.org' in "
                  "local_settings.py")
        except ValueError as ve:
            print(ve)
