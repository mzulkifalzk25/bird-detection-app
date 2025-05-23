from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a test user for development purposes'

    def handle(self, *args, **options):
        try:
            # Create test user
            user = User.objects.create_user(
                email='test@example.com',
                username='testuser',
                password='testpass123',
                first_name='Test',
                last_name='User',
                date_of_birth=date(1990, 1, 1),
                location='Test Location',
                is_email_verified=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created test user:\n'
                    f'Email: test@example.com\n'
                    f'Password: testpass123\n'
                    f'Username: testuser'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating test user: {str(e)}')
            )