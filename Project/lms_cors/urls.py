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

router = DefaultRouter()

# Academic Structure (Top-Level: Institution)
router.register(r'institutions', InstitutionViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'academic-sessions', AcademicSessionViewSet)  # NEW: Session/Batch management
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

urlpatterns = [
    path('', include(router.urls)),
]

"""
COMPLETE LMS API ENDPOINTS DOCUMENTATION
=========================================

BASE URL: /api/

## ACADEMIC STRUCTURE
----------------------

### Institutions (Top-Level Entity)
- GET/POST    /api/institutions/                   - List/Create institutions
- GET/PUT/PATCH/DELETE /api/institutions/{id}/     - Institution operations
- GET         /api/institutions/{id}/departments/  - Get institution departments
- GET         /api/institutions/{id}/statistics/   - Get institution statistics
- GET         /api/institutions/active/            - Get active institutions
- POST        /api/institutions/{id}/toggle-active/ - Toggle active status

### Departments
- GET/POST    /api/departments/                    - List/Create departments
- GET/PUT/PATCH/DELETE /api/departments/{id}/      - Department operations
- GET         /api/departments/{id}/programs/      - Get department programs
- GET         /api/departments/{id}/teachers/      - Get department teachers

### Programs
- GET/POST    /api/programs/                       - List/Create programs
- GET/PUT/PATCH/DELETE /api/programs/{id}/         - Program operations
- GET         /api/programs/{id}/semesters/        - Get program semesters (legacy)
- GET         /api/programs/{id}/students/         - Get program students (legacy)
- GET         /api/programs/{id}/sessions/         - Get program sessions (NEW)

### Academic Sessions (Batch/Intake Management) ✨ NEW
- GET/POST    /api/academic-sessions/              - List/Create sessions
- GET/PUT/PATCH/DELETE /api/academic-sessions/{id}/ - Session operations
- GET         /api/academic-sessions/{id}/semesters/ - Get session semesters
- GET         /api/academic-sessions/{id}/students/  - Get session students
- POST        /api/academic-sessions/{id}/setup-semesters/ - Auto-create semesters
- GET         /api/academic-sessions/active-sessions/ - Get active sessions
- GET         /api/academic-sessions/upcoming-sessions/ - Get upcoming sessions
- GET         /api/academic-sessions/program-sessions/?program={id} - Get sessions by program
- GET         /api/academic-sessions/{id}/statistics/ - Get session statistics
- POST        /api/academic-sessions/{id}/activate/ - Activate session
- POST        /api/academic-sessions/{id}/complete/ - Mark session as completed
- POST        /api/academic-sessions/{id}/archive/  - Archive session
- GET         /api/academic-sessions/program-levels/ - Get available program levels

### Semesters
- GET/POST    /api/semesters/                      - List/Create semesters
- GET/PUT/PATCH/DELETE /api/semesters/{id}/        - Semester operations
- GET         /api/semesters/{id}/subjects/        - Get semester subjects
- GET         /api/semesters/{id}/student-enrollments/ - Get semester enrollments

### Subjects
- GET/POST    /api/subjects/                       - List/Create subjects
- GET/PUT/PATCH/DELETE /api/subjects/{id}/         - Subject operations
- GET         /api/subjects/{id}/assignments/      - Get subject assignments
- GET         /api/subjects/{id}/enrolled-students/ - Get enrolled students
- GET         /api/subjects/{id}/assigned-teachers/ - Get assigned teachers
- GET         /api/subjects/{id}/attendance/       - Get subject attendance

## PEOPLE MANAGEMENT
---------------------
### Students
- GET/POST    /api/students/                       - List/Create students
- GET/PUT/PATCH/DELETE /api/students/{id}/         - Student operations
- POST        /api/students/{id}/activate/         - Activate student
- POST        /api/students/{id}/deactivate/       - Deactivate student
- POST        /api/students/{id}/suspend/          - Suspend student
- POST        /api/students/{id}/verify/           - Verify student
- POST        /api/students/{id}/reset-password/   - Reset password
- POST        /api/students/{id}/create-user-account/ - Create user account
- GET         /api/students/active/                - Get active students
- GET         /api/students/suspended/             - Get suspended students
- GET         /api/students/verified/              - Get verified students
- GET         /api/students/{id}/submissions/      - Get student submissions
- GET         /api/students/{id}/grades/           - Get student grades
- GET         /api/students/{id}/attendance/       - Get student attendance
- GET         /api/students/{id}/enrolled-subjects/ - Get enrolled subjects

### Teachers
- GET/POST    /api/teachers/                       - List/Create teachers
- GET/PUT/PATCH/DELETE /api/teachers/{id}/         - Teacher operations
- POST        /api/teachers/{id}/activate/         - Activate teacher
- POST        /api/teachers/{id}/deactivate/       - Deactivate teacher
- POST        /api/teachers/{id}/suspend/          - Suspend teacher
- POST        /api/teachers/{id}/verify/           - Verify teacher
- POST        /api/teachers/{id}/reset-password/   - Reset password
- POST        /api/teachers/{id}/create-user-account/ - Create user account
- GET         /api/teachers/active/                - Get active teachers
- GET         /api/teachers/suspended/             - Get suspended teachers
- GET         /api/teachers/verified/              - Get verified teachers
- GET         /api/teachers/{id}/teaching-subjects/ - Get teaching subjects
- GET         /api/teachers/{id}/created-assignments/ - Get created assignments
- GET         /api/teachers/{id}/graded-assignments/ - Get graded assignments
- GET         /api/teachers/{id}/marked-attendance/ - Get marked attendance

### Admins
- GET/POST    /api/admins/                         - List/Create admins
- GET/PUT/PATCH/DELETE /api/admins/{id}/           - Admin operations
- POST        /api/admins/{id}/activate/           - Activate admin
- POST        /api/admins/{id}/deactivate/         - Deactivate admin
- POST        /api/admins/{id}/suspend/            - Suspend admin
- POST        /api/admins/{id}/verify/             - Verify admin
- POST        /api/admins/{id}/reset-password/     - Reset password
- POST        /api/admins/{id}/create-user-account/ - Create user account
- GET         /api/admins/active/                  - Get active admins
- GET         /api/admins/suspended/               - Get suspended admins
- GET         /api/admins/verified/                - Get verified admins
- GET         /api/admins/{id}/created-events/     - Get created events

## JUNCTION TABLES
-------------------
### Teacher Subjects
- GET/POST    /api/teacher-subjects/               - List/Create teacher-subject assignments
- GET/PUT/PATCH/DELETE /api/teacher-subjects/{id}/ - Assignment operations

### Student Subjects
- GET/POST    /api/student-subjects/               - List/Create student enrollments
- GET/PUT/PATCH/DELETE /api/student-subjects/{id}/ - Enrollment operations

## ACADEMIC MANAGEMENT
-----------------------
### Assignments
- GET/POST    /api/assignments/                    - List/Create assignments
- GET/PUT/PATCH/DELETE /api/assignments/{id}/      - Assignment operations
- GET         /api/assignments/{id}/submissions/   - Get assignment submissions

### Submissions
- GET/POST    /api/submissions/                    - List/Create submissions
- GET/PUT/PATCH/DELETE /api/submissions/{id}/      - Submission operations
- GET         /api/submissions/{id}/grade/         - Get submission grade

### Grades
- GET/POST    /api/grades/                         - List/Create grades
- GET/PUT/PATCH/DELETE /api/grades/{id}/           - Grade operations

### Attendance
- GET/POST    /api/attendance/                     - List/Create attendance records
- GET/PUT/PATCH/DELETE /api/attendance/{id}/       - Attendance operations
- GET         /api/attendance/today/               - Get today's attendance

## ADMINISTRATION
------------------
### Events
- GET/POST    /api/events/                         - List/Create events
- GET/PUT/PATCH/DELETE /api/events/{id}/           - Event operations
- GET         /api/events/upcoming/                - Get upcoming events
- GET         /api/events/past/                    - Get past events
- GET         /api/events/this-month/              - Get this month's events

## FILTERING & SEARCHING
-------------------------
All list endpoints support:
- **Search**: Use `?search=term` for full-text search
- **Filtering**: Use `?field=value` for exact matches
- **Ordering**: Use `?ordering=field` or `?ordering=-field` for descending
- **Pagination**: Automatic pagination with `?page=number`

## EXAMPLE QUERIES:
-------------------
- Get students in a session: `/api/students/?academic_session={session_id}`
- Get active sessions: `/api/academic-sessions/active-sessions/`
- Auto-create semesters: `POST /api/academic-sessions/{id}/setup-semesters/`
- Get sessions for a program: `/api/academic-sessions/program-sessions/?program={program_id}`
- Get session statistics: `/api/academic-sessions/{id}/statistics/`
- Get students in a program: `/api/students/?program={program_id}`
- Get active teachers: `/api/teachers/active/`
- Get assignments for a subject: `/api/subjects/{id}/assignments/`
- Get today's attendance: `/api/attendance/today/`
- Search students by name: `/api/students/?search=John`
- Order students by enrollment: `/api/students/?ordering=-enrollment_number`
"""

"""
COMPLETE LMS API ENDPOINTS DOCUMENTATION
=========================================

BASE URL: /api/

## ACADEMIC STRUCTURE
----------------------

### Institutions (Top-Level Entity)
- GET/POST    /api/institutions/                   - List/Create institutions
- GET/PUT/PATCH/DELETE /api/institutions/{id}/     - Institution operations
- GET         /api/institutions/{id}/departments/  - Get institution departments
- GET         /api/institutions/{id}/statistics/   - Get institution statistics
- GET         /api/institutions/active/            - Get active institutions
- POST        /api/institutions/{id}/toggle-active/ - Toggle active status

### Departments
- GET/POST    /api/departments/                    - List/Create departments
- GET/PUT/PATCH/DELETE /api/departments/{id}/      - Department operations
- GET         /api/departments/{id}/programs/      - Get department programs
- GET         /api/departments/{id}/teachers/      - Get department teachers

### Programs
- GET/POST    /api/programs/                       - List/Create programs
- GET/PUT/PATCH/DELETE /api/programs/{id}/         - Program operations
- GET         /api/programs/{id}/semesters/        - Get program semesters
- GET         /api/programs/{id}/students/         - Get program students

### Semesters
- GET/POST    /api/semesters/                      - List/Create semesters
- GET/PUT/PATCH/DELETE /api/semesters/{id}/        - Semester operations
- GET         /api/semesters/{id}/subjects/        - Get semester subjects
- GET         /api/semesters/{id}/student-enrollments/ - Get semester enrollments

### Subjects
- GET/POST    /api/subjects/                       - List/Create subjects
- GET/PUT/PATCH/DELETE /api/subjects/{id}/         - Subject operations
- GET         /api/subjects/{id}/assignments/      - Get subject assignments
- GET         /api/subjects/{id}/enrolled-students/ - Get enrolled students
- GET         /api/subjects/{id}/assigned-teachers/ - Get assigned teachers
- GET         /api/subjects/{id}/attendance/       - Get subject attendance

## PEOPLE MANAGEMENT
---------------------
### Students
- GET/POST    /api/students/                       - List/Create students
- GET/PUT/PATCH/DELETE /api/students/{id}/         - Student operations
- POST        /api/students/{id}/activate/         - Activate student
- POST        /api/students/{id}/deactivate/       - Deactivate student
- POST        /api/students/{id}/suspend/          - Suspend student
- POST        /api/students/{id}/verify/           - Verify student
- POST        /api/students/{id}/reset-password/   - Reset password
- POST        /api/students/{id}/create-user-account/ - Create user account
- GET         /api/students/active/                - Get active students
- GET         /api/students/suspended/             - Get suspended students
- GET         /api/students/verified/              - Get verified students
- GET         /api/students/{id}/submissions/      - Get student submissions
- GET         /api/students/{id}/grades/           - Get student grades
- GET         /api/students/{id}/attendance/       - Get student attendance
- GET         /api/students/{id}/enrolled-subjects/ - Get enrolled subjects

### Teachers
- GET/POST    /api/teachers/                       - List/Create teachers
- GET/PUT/PATCH/DELETE /api/teachers/{id}/         - Teacher operations
- POST        /api/teachers/{id}/activate/         - Activate teacher
- POST        /api/teachers/{id}/deactivate/       - Deactivate teacher
- POST        /api/teachers/{id}/suspend/          - Suspend teacher
- POST        /api/teachers/{id}/verify/           - Verify teacher
- POST        /api/teachers/{id}/reset-password/   - Reset password
- POST        /api/teachers/{id}/create-user-account/ - Create user account
- GET         /api/teachers/active/                - Get active teachers
- GET         /api/teachers/suspended/             - Get suspended teachers
- GET         /api/teachers/verified/              - Get verified teachers
- GET         /api/teachers/{id}/teaching-subjects/ - Get teaching subjects
- GET         /api/teachers/{id}/created-assignments/ - Get created assignments
- GET         /api/teachers/{id}/graded-assignments/ - Get graded assignments
- GET         /api/teachers/{id}/marked-attendance/ - Get marked attendance

### Admins
- GET/POST    /api/admins/                         - List/Create admins
- GET/PUT/PATCH/DELETE /api/admins/{id}/           - Admin operations
- POST        /api/admins/{id}/activate/           - Activate admin
- POST        /api/admins/{id}/deactivate/         - Deactivate admin
- POST        /api/admins/{id}/suspend/            - Suspend admin
- POST        /api/admins/{id}/verify/             - Verify admin
- POST        /api/admins/{id}/reset-password/     - Reset password
- POST        /api/admins/{id}/create-user-account/ - Create user account
- GET         /api/admins/active/                  - Get active admins
- GET         /api/admins/suspended/               - Get suspended admins
- GET         /api/admins/verified/                - Get verified admins
- GET         /api/admins/{id}/created-events/     - Get created events

## JUNCTION TABLES
-------------------
### Teacher Subjects
- GET/POST    /api/teacher-subjects/               - List/Create teacher-subject assignments
- GET/PUT/PATCH/DELETE /api/teacher-subjects/{id}/ - Assignment operations

### Student Subjects
- GET/POST    /api/student-subjects/               - List/Create student enrollments
- GET/PUT/PATCH/DELETE /api/student-subjects/{id}/ - Enrollment operations

## ACADEMIC MANAGEMENT
-----------------------
### Assignments
- GET/POST    /api/assignments/                    - List/Create assignments
- GET/PUT/PATCH/DELETE /api/assignments/{id}/      - Assignment operations
- GET         /api/assignments/{id}/submissions/   - Get assignment submissions

### Submissions
- GET/POST    /api/submissions/                    - List/Create submissions
- GET/PUT/PATCH/DELETE /api/submissions/{id}/      - Submission operations
- GET         /api/submissions/{id}/grade/         - Get submission grade

### Grades
- GET/POST    /api/grades/                         - List/Create grades
- GET/PUT/PATCH/DELETE /api/grades/{id}/           - Grade operations

### Attendance
- GET/POST    /api/attendance/                     - List/Create attendance records
- GET/PUT/PATCH/DELETE /api/attendance/{id}/       - Attendance operations
- GET         /api/attendance/today/               - Get today's attendance

## ADMINISTRATION
------------------
### Events
- GET/POST    /api/events/                         - List/Create events
- GET/PUT/PATCH/DELETE /api/events/{id}/           - Event operations
- GET         /api/events/upcoming/                - Get upcoming events
- GET         /api/events/past/                    - Get past events
- GET         /api/events/this-month/              - Get this month's events

## FILTERING & SEARCHING
-------------------------
All list endpoints support:
- **Search**: Use `?search=term` for full-text search
- **Filtering**: Use `?field=value` for exact matches
- **Ordering**: Use `?ordering=field` or `?ordering=-field` for descending
- **Pagination**: Automatic pagination with `?page=number`

## EXAMPLE QUERIES:
-------------------
- Get students in a program: `/api/students/?program={program_id}`
- Get active teachers: `/api/teachers/active/`
- Get assignments for a subject: `/api/subjects/{id}/assignments/`
- Get today's attendance: `/api/attendance/today/`
- Search students by name: `/api/students/?search=John`
- Order students by enrollment: `/api/students/?ordering=-enrollment_number`
"""