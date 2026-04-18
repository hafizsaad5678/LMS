"""
Business Logic Services for LMS
Includes SemesterFactory for auto-creating semesters and other utilities
"""
from datetime import datetime
from django.db import transaction


# Program Type Configuration Rules
PROGRAM_RULES = {
    'bachelor': {
        'semesters': 8,
        'min_credits': 120,
        'max_credits': 140,
        'requires_thesis': False,
        'requires_internship': True,
        'system': 'semester',
        'duration_months_per_semester': 6
    },
    'master': {
        'semesters': 4,
        'min_credits': 30,
        'max_credits': 36,
        'requires_thesis': True,
        'requires_internship': False,
        'system': 'semester',
        'duration_months_per_semester': 6
    },
    'intermediate': {
        'parts': 4,
        'min_credits': 0,
        'max_credits': 0,
        'requires_thesis': False,
        'requires_internship': False,
        'system': 'annual',
        'duration_months_per_part': 12
    },
    'phd': {
        'semesters': 6,
        'min_credits': 60,
        'max_credits': 72,
        'requires_thesis': True,
        'requires_internship': False,
        'system': 'semester',
        'variable': True,
        'duration_months_per_semester': 6
    },
    'diploma': {
        'semesters': 2,
        'min_credits': 30,
        'max_credits': 60,
        'requires_thesis': False,
        'requires_internship': True,
        'system': 'semester',
        'variable': True,
        'duration_months_per_semester': 6
    }
}


class SemesterFactory:
    """Auto-create semesters based on program type and academic system"""
    
    @staticmethod
    @transaction.atomic
    def create_semesters_for_session(academic_session):
        """Create semesters based on program type and academic system"""
        program = academic_session.program
        
        if program.duration_years:
            target_count = program.duration_years * 2
        elif program.default_semesters:
            target_count = program.default_semesters
        else:
            if program.program_level == 'master':
                target_count = 4
            elif program.program_level == 'diploma':
                target_count = 2
            else:
                target_count = 8
        
        # Use annual system for intermediate, semester system for others
        if program.program_level == 'intermediate':
            return SemesterFactory._create_annual_parts(academic_session, target_count)
        else:
            return SemesterFactory._create_semester_based(academic_session, target_count)
    
    @staticmethod
    def _create_semester_based(session, count):
        """
        Create semesters for semester-based programs (BS, MS, PhD, Diploma, etc.)
        Unified method replacing duplicate _create_bachelor/master/phd/diploma_semesters
        """
        from ..models import Semester
        semesters = []
        
        for i in range(count):
            semester_num = i + 1
            semester_type = 'Fall' if i % 2 == 0 else 'Spring'
            # Academic cycle year (Fall starts cycle, Spring ends it in next calendar year).
            cycle_year = session.start_year + (i // 2)
            
            if i % 2 == 0:
                display_year = cycle_year
                sem_start = datetime(display_year, 9, 1).date()
                sem_end = datetime(display_year, 12, 31).date()
            else:
                display_year = cycle_year + 1
                sem_start = datetime(display_year, 3, 1).date()
                sem_end = datetime(display_year, 6, 30).date()
            
            semester = Semester.objects.create(
                session=session,
                program=session.program,
                number=semester_num,
                name=f"Semester {semester_num} ({semester_type} {display_year})",
                start_date=sem_start,
                end_date=sem_end,
                status='draft'
            )
            semesters.append(semester)
        
        return semesters
    
    @staticmethod
    def _create_annual_parts(session, count=4):
        """Create parts for FSC/Intermediate (Annual System - 2 years, 4 parts)"""
        from ..models import Semester
        semesters = []
        
        for i in range(count):
            part_num = i + 1
            year_offset = i // 2
            year = session.start_year + year_offset
            
            if i % 2 == 0:
                sem_start = datetime(year, 7, 1).date()
                sem_end = datetime(year, 12, 31).date()
            else:
                sem_start = datetime(year, 1, 1).date()
                sem_end = datetime(year, 6, 30).date()
            
            semester = Semester.objects.create(
                session=session,
                program=session.program,
                number=part_num,
                name=f"Part {part_num} (Year {year_offset + 1})",
                start_date=sem_start,
                end_date=sem_end,
                status='draft'
            )
            semesters.append(semester)
        
        return semesters


class EnrollmentService:
    """Handle student enrollment validation and operations"""
    
    @staticmethod
    def validate_session_enrollment(student, academic_session):
        """Validate if a student can be enrolled in a session"""
        if academic_session.is_full:
            return False, f"Session {academic_session.session_name} is at full capacity"
        
        if academic_session.status not in ['active', 'upcoming']:
            return False, f"Session {academic_session.session_name} is not accepting enrollments"
        
        if student.academic_session and student.academic_session != academic_session:
            return False, f"Student is already enrolled in {student.academic_session.session_name}"
        
        if academic_session.admission_end_date:
            from django.utils import timezone
            today = timezone.now().date()
            if today > academic_session.admission_end_date:
                return False, f"Admission period for {academic_session.session_name} has ended"
        
        return True, None
    
    @staticmethod
    def calculate_enrollment_stats(academic_session):
        """Calculate enrollment statistics for a session"""
        total_students = academic_session.students.count()
        capacity_used = (total_students / academic_session.total_capacity * 100) if academic_session.total_capacity > 0 else 0
        
        return {
            'total_students': total_students,
            'total_capacity': academic_session.total_capacity,
            'available_seats': academic_session.total_capacity - total_students,
            'capacity_percentage': round(capacity_used, 2),
            'is_full': total_students >= academic_session.total_capacity
        }


class ProgramTypeValidator:
    """Validate program configurations based on type"""
    
    @staticmethod
    def validate_program_config(program):
        """Validate program configuration based on program level"""
        errors = []
        
        if not program.program_level:
            errors.append("Program level is required")
            return False, errors
        
        rules = PROGRAM_RULES.get(program.program_level)
        if not rules:
            errors.append(f"Unknown program level: {program.program_level}")
            return False, errors
        
        expected_semesters = rules.get('semesters') or rules.get('parts')
        if program.default_semesters != expected_semesters and not rules.get('variable'):
            errors.append(
                f"{program.program_level.title()} programs should have {expected_semesters} semesters/parts, "
                f"but {program.default_semesters} is configured"
            )
        
        if program.min_credit_hours and program.max_credit_hours:
            if program.min_credit_hours > program.max_credit_hours:
                errors.append("Minimum credit hours cannot be greater than maximum")
        
        if rules.get('requires_thesis') and not program.requires_thesis:
            errors.append(f"{program.program_level.title()} programs typically require a thesis")
        
        if rules.get('requires_internship') and not program.requires_internship:
            errors.append(f"{program.program_level.title()} programs typically require an internship")
        
        return len(errors) == 0, errors
