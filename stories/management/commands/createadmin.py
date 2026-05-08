from django.core.management.base import BaseCommand
from stories.models import User


class Command(BaseCommand):
    help = 'Создание главного администратора'

    def handle(self, *args, **kwargs):
        email = 'areg.dzharayan@bk.ru'
        password = 'Admin12345!'

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING('Админ уже существует')
            )
            return

        user = User.objects.create_superuser(
            email=email,
            password=password
        )

        user.is_admin_owner = True
        user.email_verified = True
        user.username = email

        user.save()

        self.stdout.write(
            self.style.SUCCESS('Админ успешно создан')
        )