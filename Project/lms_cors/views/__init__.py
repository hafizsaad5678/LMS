# Views Package - Import all viewsets
from .base import BaseViewSet, BaseProfileViewSet
from .academic import (
    InstitutionViewSet, DepartmentViewSet, ProgramViewSet,
    AcademicSessionViewSet, SemesterViewSet, SubjectViewSet
)
from .people import (
    StudentViewSet, TeacherViewSet, AdminViewSet,
    TeacherSubjectViewSet, StudentSubjectViewSet
)
from .assignments import AssignmentViewSet, SubmissionHistoryViewSet, GradeViewSet
from .attendance import AttendanceViewSet
from .scheduling import EventViewSet, HolidayViewSet, ExamViewSet, TimetableViewSet
from .management import FeeViewSet, ExpenseViewSet, AccountViewSet
from .library import LibraryBookViewSet, BookBorrowingViewSet
from .materials import MaterialViewSet, AnnouncementViewSet

__all__ = [
    # Base
    'BaseViewSet', 'BaseProfileViewSet',
    # Academic
    'InstitutionViewSet', 'DepartmentViewSet', 'ProgramViewSet',
    'AcademicSessionViewSet', 'SemesterViewSet', 'SubjectViewSet',
    # People
    'StudentViewSet', 'TeacherViewSet', 'AdminViewSet',
    'TeacherSubjectViewSet', 'StudentSubjectViewSet',
    # Assignments
    'AssignmentViewSet', 'SubmissionHistoryViewSet', 'GradeViewSet',
    # Attendance
    'AttendanceViewSet',
    # Scheduling
    'EventViewSet', 'HolidayViewSet', 'ExamViewSet', 'TimetableViewSet',
    # Management
    'FeeViewSet', 'ExpenseViewSet', 'AccountViewSet',
    # Library
    'LibraryBookViewSet', 'BookBorrowingViewSet',
    # Materials
    'MaterialViewSet', 'AnnouncementViewSet',
]
