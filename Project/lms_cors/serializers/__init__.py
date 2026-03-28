# Serializers Package - Import all serializers
from .academic import (
    InstitutionSerializer, InstitutionDetailSerializer,
    DepartmentSerializer, DepartmentDetailSerializer,
    ProgramSerializer, ProgramDetailSerializer,
    AcademicSessionSerializer, AcademicSessionDetailSerializer,
    SemesterSerializer, SubjectSerializer, SubjectDetailSerializer
)
from .people import (
    BaseProfileSerializer,
    StudentSerializer, StudentDetailSerializer,
    TeacherSerializer, TeacherDetailSerializer,
    AdminSerializer,
    TeacherSubjectSerializer, StudentSubjectSerializer
)
from .assignments import (
    AssignmentSerializer, SubmissionHistorySerializer, GradeSerializer, StudentAssignmentSerializer
)
from .attendance import AttendanceSerializer
from .scheduling import (
    EventSerializer, HolidaySerializer, ExamSerializer, TimetableSerializer
)
from .management import FeeSerializer, ExpenseSerializer, AccountSerializer
from .library import LibraryBookSerializer, BookBorrowingSerializer
from .materials import MaterialSerializer, AnnouncementSerializer, ActivityLogSerializer
from .grading import GradeComponentSerializer, StudentMarkSerializer, StudentGradeSummarySerializer

__all__ = [
    # Academic
    'InstitutionSerializer', 'InstitutionDetailSerializer',
    'DepartmentSerializer', 'DepartmentDetailSerializer',
    'ProgramSerializer', 'ProgramDetailSerializer',
    'AcademicSessionSerializer', 'AcademicSessionDetailSerializer',
    'SemesterSerializer', 'SubjectSerializer',
    # People
    'BaseProfileSerializer',
    'StudentSerializer', 'StudentDetailSerializer',
    'TeacherSerializer', 'TeacherDetailSerializer',
    'AdminSerializer',
    'TeacherSubjectSerializer', 'StudentSubjectSerializer',
    # Assignments
    'AssignmentSerializer', 'SubmissionHistorySerializer', 'GradeSerializer',
    # Attendance
    'AttendanceSerializer',
    # Scheduling
    'EventSerializer', 'HolidaySerializer', 'ExamSerializer', 'TimetableSerializer',
    # Management
    'FeeSerializer', 'ExpenseSerializer', 'AccountSerializer',
    # Library
    'LibraryBookSerializer', 'BookBorrowingSerializer',
    # Materials
    'MaterialSerializer', 'AnnouncementSerializer', 'ActivityLogSerializer',
    # Grading
    'GradeComponentSerializer', 'StudentMarkSerializer', 'StudentGradeSummarySerializer',
]
