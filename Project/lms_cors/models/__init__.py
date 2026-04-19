# Models Package - Import all models for Django to discover them
from .base import BaseProfile, validate_profile_image_size, profile_image_path
from .academic import (
    Institution, Department, Program, AcademicSession, 
    Semester, Subject, generate_sequential_id
)
from .people import Student, StudentSemesterHistory, Teacher, Admin, TeacherSubject, StudentSubject
from .assignments import Assignment, SubmissionHistory, Grade
from .attendance import Attendance
from .scheduling import Event, Holiday, Exam, Timetable
from .management import Fee, Expense, Account
from .library import LibraryBook, LibraryBorrowPolicy, BookBorrowing
from .materials import Material, Announcement, ActivityLog
from .grading import GradeComponent, StudentMark, StudentGradeSummary

__all__ = [
    # Base
    'BaseProfile', 'validate_profile_image_size', 'profile_image_path',
    # Academic
    'Institution', 'Department', 'Program', 'AcademicSession', 
    'Semester', 'Subject', 'generate_sequential_id',
    # People
    'Student', 'StudentSemesterHistory', 'Teacher', 'Admin', 'TeacherSubject', 'StudentSubject',
    # Assignments
    'Assignment', 'SubmissionHistory', 'Grade',
    # Attendance
    'Attendance',
    # Scheduling
    'Event', 'Holiday', 'Exam', 'Timetable',
    # Management
    'Fee', 'Expense', 'Account',
    # Library
    'LibraryBook', 'LibraryBorrowPolicy', 'BookBorrowing',
    # Materials
    'Material', 'Announcement', 'ActivityLog',
    # Grading
    'GradeComponent', 'StudentMark', 'StudentGradeSummary',
]
