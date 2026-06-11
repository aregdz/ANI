import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from stories.models import User


class Command(BaseCommand):
    help = 'Создаёт или обновляет главного администратора проекта А.Н.И.'

    def add_arguments(self, parser):
        parser.add_argument('--phone', default=settings.ADMIN_PHONE)
        parser.add_argument('--password', default=os.getenv('ANI_ADMIN_PASSWORD'))

    def handle(self, *args, **options):
        phone = options['phone']
        password = options['password']
        if not password:
            raise CommandError(
                'Передайте --password или задайте ANI_ADMIN_PASSWORD.'
            )

        user, _ = User.objects.get_or_create(
            phone=phone,
            defaults={'username': phone, 'email': f'{phone}@admin.local'},
        )
        user.username = phone
        user.is_staff = True
        user.is_superuser = True
        user.is_admin_owner = True
        user.email_verified = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Администратор готов: {phone}'))
