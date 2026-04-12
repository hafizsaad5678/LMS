from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InstitutionViewSet, DepartmentViewSet, ProgramViewSet, AcademicSessionViewSet,
    SemesterViewSet, SubjectViewSet,
    StudentViewSet, TeacherViewSet, AdminViewSet,
    TeacherSubjectViewSet, StudentSubjectViewSet,
    AssignmentViewSet, SubmissionHistoryViewSet, GradeViewSet, AttendanceViewSet,
    EventViewSet, HolidayViewSet, ExamViewSet, TimetableViewSet,
    FeeViewSet, ExpenseViewSet, AccountViewSet,
    LibraryBookViewSet, BookBorrowingViewSet
)
from .views.grading import (
    GradeComponentViewSet, StudentMarkViewSet, 
    QuizViewSet, QuizQuestionViewSet, QuizAttemptViewSet
)
from .views.people import teacher_my_classes, teacher_my_assignments, teacher_class_students
from .views.scheduling import teacher_timetable, teacher_exams, teacher_attendance_report
from .views.materials import (
    MaterialViewSet, AnnouncementViewSet, teacher_materials, teacher_announcements,
    create_material, create_announcement, activity_logs, ping
)
from .views.public import public_stats, submit_contact, submit_feedback

router = DefaultRouter()

# Academic Structure
router.register(r'institutions', InstitutionViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'academic-sessions', AcademicSessionViewSet)
router.register(r'semesters', SemesterViewSet)
router.register(r'subjects', SubjectViewSet)

# People
router.register(r'students', StudentViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'admins', AdminViewSet)

# Junction Tables
router.register(r'teacher-subjects', TeacherSubjectViewSet)
router.register(r'student-subjects', StudentSubjectViewSet)

# Academic Management
router.register(r'assignments', AssignmentViewSet)
router.register(r'submissions', SubmissionHistoryViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'quiz-questions', QuizQuestionViewSet, basename='quiz-question')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')
router.register(r'grade-components', GradeComponentViewSet, basename='grade-component')
router.register(r'student-marks', StudentMarkViewSet, basename='student-mark')
router.register(r'attendance', AttendanceViewSet)

# Academic Scheduling
router.register(r'events', EventViewSet)
router.register(r'holidays', HolidayViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'timetables', TimetableViewSet)

# Management/Financial
router.register(r'fees', FeeViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'accounts', AccountViewSet)

# Library
router.register(r'library-books', LibraryBookViewSet)
router.register(r'book-borrowings', BookBorrowingViewSet)

# Materials & Announcements
router.register(r'materials', MaterialViewSet)
router.register(r'announcements', AnnouncementViewSet)

urlpatterns = [
    path('teacher/my-classes/', teacher_my_classes, name='teacher-my-classes'),
    path('teacher/my-assignments/', teacher_my_assignments, name='teacher-my-assignments'),
    path('teacher/class/<str:class_id>/students/', teacher_class_students, name='teacher-class-students'),
    path('teacher/timetable/', teacher_timetable, name='teacher-timetable'),
    path('teacher/exams/', teacher_exams, name='teacher-exams'),
    path('teacher/attendance-report/', teacher_attendance_report, name='teacher-attendance-report'),
    path('teacher/materials/', teacher_materials, name='teacher-materials'),
    path('teacher/announcements/', teacher_announcements, name='teacher-announcements'),
    path('teacher/materials/create/', create_material, name='create-material'),
    path('teacher/announcements/create/', create_announcement, name='create-announcement'),
    path('ping/', ping, name='ping'),
    path('admin/activity-logs/', activity_logs, name='activity-logs'),
    
    # Public Stats / Forms
    path('public/stats/', public_stats, name='public-stats'),
    path('public/contact/', submit_contact, name='public-contact'),
    path('public/feedback/', submit_feedback, name='public-feedback'),
    
    path('', include(router.urls)),
]
