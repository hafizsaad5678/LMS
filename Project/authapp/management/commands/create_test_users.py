from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authapp.models import UserProfile

class Command(BaseCommand):
    help = 'Create test users with different roles'

    def handle(self, *args, **options):
        # Delete existing test users
        User.objects.filter(username__in=['admin@test.com', 'teacher@test.com', 'student@test.com']).delete()
        
        # Create admin user
        admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        UserProfile.objects.create(user=admin_user, role='admin')
        self.stdout.write(self.style.SUCCESS('✅ Created admin user: admin@test.com / admin123'))
        
        # Create teacher user
        teacher_user = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='teacher123',
            first_name='Teacher',
            last_name='User'
        )
        UserProfile.objects.create(user=teacher_user, role='instructor')
        self.stdout.write(self.style.SUCCESS('✅ Created teacher user: teacher@test.com / teacher123'))
        
        # Create student user
        student_user = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='student123',
            first_name='Student',
            last_name='User'
        )
        UserProfile.objects.create(user=student_user, role='student')
        self.stdout.write(self.style.SUCCESS('✅ Created student user: student@test.com / student123'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ All test users created successfully!'))
        self.stdout.write('\nTest Credentials:')
        self.stdout.write('Admin:    admin@test.com / admin123')
        self.stdout.write('Teacher:  teacher@test.com / teacher123')
        self.stdout.write('Student:  student@test.com / student123')
