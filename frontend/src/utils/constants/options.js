/**
 * Shared Dropdown Options Constants
 * Centralized options for dropdowns across all panels
 */

// Gender options
export const GENDER_OPTIONS = [
    { value: 'male', label: 'Male' },
    { value: 'female', label: 'Female' },
    { value: 'other', label: 'Other' }
]

// Teacher designation options
export const DESIGNATION_OPTIONS = [
    { value: 'Professor', label: 'Professor' },
    { value: 'Associate Professor', label: 'Associate Professor' },
    { value: 'Assistant Professor', label: 'Assistant Professor' },
    { value: 'Lecturer', label: 'Lecturer' },
    { value: 'Lab Instructor', label: 'Lab Instructor' },
    { value: 'Teaching Assistant', label: 'Teaching Assistant' }
]

// Assessment/Grade component types
export const ASSESSMENT_TYPES = [
    { value: 'assignment', label: 'Assignment' },
    { value: 'quiz', label: 'Quiz' },
    { value: 'midterm', label: 'Midterm Exam' },
    { value: 'final', label: 'Final Exam' },
    { value: 'project', label: 'Project' },
    { value: 'participation', label: 'Class Participation' },
    { value: 'lab', label: 'Lab Work' },
    { value: 'presentation', label: 'Presentation' },
    { value: 'custom', label: 'Custom' }
]

// Priority levels
export const PRIORITY_OPTIONS = [
    { value: 'high', label: 'High Priority' },
    { value: 'medium', label: 'Medium Priority' },
    { value: 'low', label: 'Low Priority' }
]

// Status options (generic)
export const STATUS_OPTIONS = [
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'pending', label: 'Pending' }
]

// Attendance status options
export const ATTENDANCE_STATUS_OPTIONS = [
    { value: 'present', label: 'Present' },
    { value: 'absent', label: 'Absent' },
    { value: 'late', label: 'Late' },
    { value: 'excused', label: 'Excused' }
]

// Attendance filter options (for student view, alias of ATTENDANCE_STATUS_OPTIONS)
export const ATTENDANCE_FILTER_OPTIONS = ATTENDANCE_STATUS_OPTIONS

// Assignment status options
export const ASSIGNMENT_STATUS_OPTIONS = [
    { value: 'pending', label: 'Pending' },
    { value: 'submitted', label: 'Submitted' },
    { value: 'graded', label: 'Graded' },
    { value: 'late', label: 'Late' },
    { value: 'missing', label: 'Missing' }
]

// Submission status filter options
export const SUBMISSION_STATUS_OPTIONS = [
    { value: 'submitted', label: 'Submitted' },
    { value: 'graded', label: 'Graded' },
    { value: 'pending', label: 'Pending Grade' }
]

// Assignment filter options (for student view)
// Assignment filter options (for student view)
export const ASSIGNMENT_FILTER_OPTIONS = [
    { value: 'all', label: 'All Assignments' },
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'pending', label: 'Pending' },
    { value: 'submitted', label: 'Submitted' },
    { value: 'overdue', label: 'Overdue' }
]

// Exam status filter options
export const EXAM_STATUS_OPTIONS = [
    { value: 'upcoming', label: 'Upcoming' },
    { value: 'completed', label: 'Completed' }
]

// Submission status options for teacher
export const TEACHER_SUBMISSION_STATUS_OPTIONS = [
    { value: 'graded', label: 'Graded' },
    { value: 'submitted', label: 'Submitted (Not Graded)' }
]

// Announcement priority options
export const ANNOUNCEMENT_PRIORITY_OPTIONS = [
    { value: 'urgent', label: 'Urgent' },
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' }
]

// Exam type options
export const EXAM_TYPE_OPTIONS = [
    { value: 'midterm', label: 'Midterm' },
    { value: 'final', label: 'Final' },
    { value: 'quiz', label: 'Quiz' },
    { value: 'practical', label: 'Practical' },
    { value: 'viva', label: 'Viva/Oral' }
]

// Exam/Schedule status options
export const SCHEDULE_STATUS_OPTIONS = [
    { value: 'scheduled', label: 'Scheduled' },
    { value: 'ongoing', label: 'Ongoing' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' }
]

// Grade report period options
export const GRADE_PERIOD_OPTIONS = [
    { value: 'current', label: 'Current Semester' },
    { value: 'midterm', label: 'Midterm' },
    { value: 'final', label: 'Final' }
]

// Session/Semester status options
export const SESSION_STATUS_OPTIONS = [
    { value: 'upcoming', label: 'Upcoming' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
    { value: 'archived', label: 'Archived' }
]

// Semester status options (includes draft)
export const SEMESTER_STATUS_OPTIONS = [
    { value: 'draft', label: 'Draft' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
    { value: 'archived', label: 'Archived' }
]

// Time-based status filters for events
export const EVENT_TIME_STATUS_OPTIONS = [
    { value: 'upcoming', label: 'Upcoming' },
    { value: 'today', label: 'Today' },
    { value: 'past', label: 'Past' }
]

// Assignment time status filters
export const ASSIGNMENT_TIME_STATUS_OPTIONS = [
    { value: 'upcoming', label: 'Upcoming' },
    { value: 'overdue', label: 'Overdue' }
]

// Event type options
export const EVENT_TYPE_OPTIONS = [
    { value: 'academic', label: 'Academic' },
    { value: 'cultural', label: 'Cultural' },
    { value: 'sports', label: 'Sports' },
    { value: 'seminar', label: 'Seminar' },
    { value: 'workshop', label: 'Workshop' },
    { value: 'holiday', label: 'Holiday' },
    { value: 'exam', label: 'Examination' },
    { value: 'other', label: 'Other' }
]

// Blood group options
export const BLOOD_GROUP_OPTIONS = [
    { value: 'a+', label: 'A+' },
    { value: 'a-', label: 'A-' },
    { value: 'b+', label: 'B+' },
    { value: 'b-', label: 'B-' },
    { value: 'ab+', label: 'AB+' },
    { value: 'ab-', label: 'AB-' },
    { value: 'o+', label: 'O+' },
    { value: 'o-', label: 'O-' },
    { value: 'unknown', label: 'Unknown' }
]

// Account type options
export const ACCOUNT_TYPE_OPTIONS = [
    { value: 'bank', label: 'Bank Account' },
    { value: 'cash', label: 'Cash' },
    { value: 'petty_cash', label: 'Petty Cash' },
    { value: 'other', label: 'Other' }
]

// Expense category options
export const EXPENSE_CATEGORY_OPTIONS = [
    { value: 'utilities', label: 'Utilities' },
    { value: 'salaries', label: 'Salaries' },
    { value: 'maintenance', label: 'Maintenance' },
    { value: 'equipment', label: 'Equipment' },
    { value: 'supplies', label: 'Supplies' },
    { value: 'other', label: 'Other' }
]

// Expense approval status options
export const EXPENSE_APPROVAL_OPTIONS = [
    { value: 'approved', label: 'Approved' },
    { value: 'pending', label: 'Pending' }
]

// Fee payment status options
export const FEE_STATUS_OPTIONS = [
    { value: 'paid', label: 'Paid' },
    { value: 'pending', label: 'Pending' },
    { value: 'overdue', label: 'Overdue' }
]

// Common semester quick options
export const SEMESTER_NUMBER_OPTIONS = [
    { value: '1', label: 'Semester 1' },
    { value: '2', label: 'Semester 2' }
]

// Library catalog category options
export const BOOK_CATEGORY_OPTIONS = [
    { value: 'science', label: 'Science' },
    { value: 'technology', label: 'Technology' },
    { value: 'arts', label: 'Arts' },
    { value: 'literature', label: 'Literature' },
    { value: 'history', label: 'History' }
]

// Library borrowing status options
export const BORROWING_STATUS_OPTIONS = [
    { value: 'borrowed', label: 'Borrowed' },
    { value: 'returned', label: 'Returned' },
    { value: 'overdue', label: 'Overdue' }
]

// Course duration filter options
export const COURSE_DURATION_OPTIONS = [
    { value: '2', label: '2 Years' },
    { value: '3', label: '3 Years' },
    { value: '4', label: '4 Years' },
    { value: '5', label: '5 Years' }
]

// Material type options
export const MATERIAL_TYPE_OPTIONS = [
    { value: 'lecture_notes', label: 'Lecture Notes' },
    { value: 'slides', label: 'Slides' },
    { value: 'assignment', label: 'Assignment' },
    { value: 'reference', label: 'Reference Material' },
    { value: 'video', label: 'Video' },
    { value: 'outline', label: 'Course Outline' },
    { value: 'datesheet', label: 'Date Sheet' },
    { value: 'other', label: 'Other' }
]

// Country options (common ones)
export const COUNTRY_OPTIONS = [
    { value: 'Pakistan', label: 'Pakistan' },
    { value: 'United States', label: 'United States' },
    { value: 'United Kingdom', label: 'United Kingdom' },
    { value: 'Canada', label: 'Canada' },
    { value: 'Australia', label: 'Australia' },
    { value: 'Other', label: 'Other' }
]

// Holiday type options
export const HOLIDAY_TYPE_OPTIONS = [
    { value: 'public', label: 'Public Holiday' },
    { value: 'academic', label: 'Academic Break' },
    { value: 'religious', label: 'Religious' },
    { value: 'national', label: 'National' }
]

// Month options for filters
export const getMonthOptions = (year = new Date().getFullYear()) => {
    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    return months.map((month, index) => ({
        value: `${year}-${String(index + 1).padStart(2, '0')}`,
        label: `${month} ${year}`
    }))
}

// Month options without year suffix (value: '01'..'12')
export const MONTH_NUMBER_OPTIONS = [
    { value: '01', label: 'January' },
    { value: '02', label: 'February' },
    { value: '03', label: 'March' },
    { value: '04', label: 'April' },
    { value: '05', label: 'May' },
    { value: '06', label: 'June' },
    { value: '07', label: 'July' },
    { value: '08', label: 'August' },
    { value: '09', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' }
]

export const getYearRangeOptions = (startOffset = 10, endOffset = 1, baseYear = new Date().getFullYear()) => {
    const result = []
    for (let year = baseYear - startOffset; year <= baseYear + endOffset; year += 1) {
        result.push({ value: String(year), label: String(year) })
    }
    return result
}

// Helper to get label from options array
export const getOptionLabel = (options, value) => {
    const option = options.find(opt => opt.value === value)
    return option ? option.label : value || 'N/A'
}

export default {
    GENDER_OPTIONS,
    DESIGNATION_OPTIONS,
    ASSESSMENT_TYPES,
    PRIORITY_OPTIONS,
    STATUS_OPTIONS,
    ATTENDANCE_STATUS_OPTIONS,
    ASSIGNMENT_STATUS_OPTIONS,
    SUBMISSION_STATUS_OPTIONS,
    ASSIGNMENT_FILTER_OPTIONS,
    EXAM_STATUS_OPTIONS,
    EXAM_TYPE_OPTIONS,
    SCHEDULE_STATUS_OPTIONS,
    GRADE_PERIOD_OPTIONS,
    SESSION_STATUS_OPTIONS,
    SEMESTER_STATUS_OPTIONS,
    EVENT_TIME_STATUS_OPTIONS,
    ASSIGNMENT_TIME_STATUS_OPTIONS,
    ANNOUNCEMENT_PRIORITY_OPTIONS,
    EVENT_TYPE_OPTIONS,
    BLOOD_GROUP_OPTIONS,
    ACCOUNT_TYPE_OPTIONS,
    EXPENSE_CATEGORY_OPTIONS,
    EXPENSE_APPROVAL_OPTIONS,
    FEE_STATUS_OPTIONS,
    SEMESTER_NUMBER_OPTIONS,
    BOOK_CATEGORY_OPTIONS,
    BORROWING_STATUS_OPTIONS,
    COURSE_DURATION_OPTIONS,
    MATERIAL_TYPE_OPTIONS,
    COUNTRY_OPTIONS,
    HOLIDAY_TYPE_OPTIONS,
    getMonthOptions,
    MONTH_NUMBER_OPTIONS,
    getYearRangeOptions,
    getOptionLabel
}
