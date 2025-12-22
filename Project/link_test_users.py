"""
Script to create/link test user profiles
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from lms_cors.models import Student, Teacher, Program, Department

# Get test users
try:
    student_user = User.objects.get(username='student')
    teacher_user = User.objects.get(username='teacher')
    
    # Check if profiles already exist
    existing_student = Student.objects.filter(user=student_user).first()
    existing_teacher = Teacher.objects.filter(user=teacher_user).first()
    
    if existing_student:
        print(f"Student profile exists: {existing_student.full_name}")
    else:
        # Create student profile
        program = Program.objects.first()
        student = Student.objects.create(
            user=student_user,
            full_name="Test Student",
            email=student_user.email,
            program=program,
            enrollment_year=2024
        )
        print(f"Created student profile: {student.full_name} ({student.enrollment_number})")
    
    if existing_teacher:
        print(f"Teacher profile exists: {existing_teacher.full_name}")
    else:
        # Create teacher profile
        department = Department.objects.first()
        teacher = Teacher.objects.create(
            user=teacher_user,
            full_name="Test Teacher",
            email=teacher_user.email,
            department=department,
            designation="Lecturer"
        )
        print(f"Created teacher profile: {teacher.full_name} ({teacher.employee_id})")
    
    print("\nTest credentials ready:")
    print("- Admin: username='admin' or 'saad' (superuser)")
    print("- Student: username='student', password=(your password)")
    print("- Teacher: username='teacher', password=(your password)")
    
except User.DoesNotExist as e:
    print(f"User not found: {e}")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
