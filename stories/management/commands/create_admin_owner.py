from django.conf import settings
from django.core.management.base import BaseCommand
from stories.models import User


class Command(BaseCommand):
    help = 'Создает единственного администратора проекта АНИ'

    def add_arguments(self, parser):
        parser.add_argument('--phone', default=settings.ADMIN_PHONE)
        parser.add_argument('--password', default=settings.ADMIN_PHONE)

    def handle(self, *args, **options):
        phone = options['phone']
        password = options['password']
        user, created = User.objects.get_or_create(phone=phone, defaults={'username': phone})
        user.username = phone
        user.is_staff = True
        user.is_superuser = True
        user.is_admin_owner = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Администратор готов: {phone} / {password}'))
