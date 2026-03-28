# Admin Package - Import all admin classes
from .base import BaseAdmin
from .academic import (
    InstitutionAdmin, DepartmentAdmin, ProgramAdmin,
    AcademicSessionAdmin, SemesterAdmin, SubjectAdmin
)
from .people import StudentAdmin, TeacherAdmin, AdminAdmin, TeacherSubjectAdmin, StudentSubjectAdmin
from .assignments import AssignmentAdmin, SubmissionHistoryAdmin, GradeAdmin
from .attendance import AttendanceAdmin
from .scheduling import EventAdmin, HolidayAdmin, ExamAdmin, TimetableAdmin
from .management import FeeAdmin, ExpenseAdmin, AccountAdmin
from .library import LibraryBookAdmin, BookBorrowingAdmin
