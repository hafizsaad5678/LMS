/**
 * Route Constants
 * Centralized route definitions for all panels
 * Use named routes instead of hard-coded strings
 */

// Admin Panel Routes
export const ADMIN_ROUTES = {
    // Dashboard
    DASHBOARD: { name: 'AdminDashboard', path: '/admin-dashboard' },

    // Institution
    INSTITUTION_LIST: { name: 'ListInstitution', path: '/admin-dashboard/institution' },
    INSTITUTION_ADD: { name: 'AddInstitution', path: '/admin-dashboard/institution/add' },
    INSTITUTION_EDIT: { name: 'EditInstitution', path: '/admin-dashboard/institution/edit' },
    INSTITUTION_PROFILE: { name: 'InstitutionProfile', path: '/admin-dashboard/institution' },

    // Department
    DEPARTMENT_LIST: { name: 'ListDepartment', path: '/admin-dashboard/departments' },
    DEPARTMENT_ADD: { name: 'AddDepartment', path: '/admin-dashboard/departments/add' },
    DEPARTMENT_EDIT: { name: 'EditDepartment', path: '/admin-dashboard/departments/edit' },
    DEPARTMENT_PROFILE: { name: 'DepartmentProfile', path: '/admin-dashboard/departments' },
    DEPARTMENT_DELETE: { name: 'DeleteDepartment', path: '/admin-dashboard/departments/delete' },

    // Course/Program
    COURSE_LIST: { name: 'ListCourse', path: '/admin-dashboard/courses' },
    COURSE_ADD: { name: 'AddCourse', path: '/admin-dashboard/courses/add' },
    COURSE_EDIT: { name: 'EditCourse', path: '/admin-dashboard/courses/edit' },
    COURSE_PROFILE: { name: 'CourseProfile', path: '/admin-dashboard/courses' },
    COURSE_DELETE: { name: 'DeleteCourse', path: '/admin-dashboard/courses/delete' },

    // Subject
    SUBJECT_LIST: { name: 'ListSubject', path: '/admin-dashboard/subjects' },
    SUBJECT_ADD: { name: 'AddSubject', path: '/admin-dashboard/subjects/add' },
    SUBJECT_EDIT: { name: 'EditSubject', path: '/admin-dashboard/subjects/edit' },
    SUBJECT_PROFILE: { name: 'SubjectProfile', path: '/admin-dashboard/subjects' },
    SUBJECT_DELETE: { name: 'DeleteSubject', path: '/admin-dashboard/subjects/delete' },

    // Student
    STUDENT_LIST: { name: 'ListStudent', path: '/admin-dashboard/students' },
    STUDENT_ADD: { name: 'AddStudent', path: '/admin-dashboard/students/add' },
    STUDENT_EDIT: { name: 'EditStudent', path: '/admin-dashboard/students/edit' },
    STUDENT_PROFILE: { name: 'StudentProfile', path: '/admin-dashboard/students' },
    STUDENT_DELETE: { name: 'DeleteStudent', path: '/admin-dashboard/students/delete' },

    // Teacher
    TEACHER_LIST: { name: 'ListTeacher', path: '/admin-dashboard/teachers' },
    TEACHER_ADD: { name: 'AddTeacher', path: '/admin-dashboard/teachers/add' },
    TEACHER_EDIT: { name: 'EditTeacher', path: '/admin-dashboard/teachers/edit' },
    TEACHER_PROFILE: { name: 'TeacherProfile', path: '/admin-dashboard/teachers' },
    TEACHER_DELETE: { name: 'DeleteTeacher', path: '/admin-dashboard/teachers/delete' },

    // Semester
    SEMESTER_LIST: { name: 'ListSemester', path: '/admin-dashboard/semesters' },
    SEMESTER_ADD: { name: 'AddSemester', path: '/admin-dashboard/semesters/add' },
    SEMESTER_EDIT: { name: 'EditSemester', path: '/admin-dashboard/semesters/edit' },
    SEMESTER_PROFILE: { name: 'SemesterProfile', path: '/admin-dashboard/semesters' },

    // Session
    SESSION_LIST: { name: 'ListSessions', path: '/admin-dashboard/sessions' },
    SESSION_ADD: { name: 'AddSession', path: '/admin-dashboard/sessions/add' },
    SESSION_EDIT: { name: 'EditSession', path: '/admin-dashboard/sessions/edit' },
    SESSION_PROFILE: { name: 'SessionProfile', path: '/admin-dashboard/sessions/profile' },

    // Library
    LIBRARY: { name: 'LibraryDashboard', path: '/admin-dashboard/library' },
    LIBRARY_BOOKS: { name: 'LibraryBooks', path: '/admin-dashboard/library/books' },
    LIBRARY_BORROWING: { name: 'BookBorrowing', path: '/admin-dashboard/library/borrowings' },

    // Management
    ACCOUNTS: { name: 'Accounts', path: '/admin-dashboard/accounts' },
    FEES: { name: 'FeesCollection', path: '/admin-dashboard/fees-collection' },
    EXPENSES: { name: 'Expenses', path: '/admin-dashboard/expenses' },

    // Academic
    EVENTS: { name: 'Events', path: '/admin-dashboard/events' },
    HOLIDAYS: { name: 'Holidays', path: '/admin-dashboard/holidays' },
    EXAMS: { name: 'ExamList', path: '/admin-dashboard/exams' },
    TIMETABLE: { name: 'TimeTable', path: '/admin-dashboard/timetable' },

    // Assignments
    ASSIGNMENTS: { name: 'ListAssignment', path: '/admin-dashboard/assignments' },
    ASSIGNMENT_ADD: { name: 'AddAssignment', path: '/admin-dashboard/assignments/add' },
    ASSIGNMENT_EDIT: { name: 'EditAssignment', path: '/admin-dashboard/assignments/edit' },
    ASSIGNMENT_DELETE: { name: 'DeleteAssignment', path: '/admin-dashboard/assignments/delete' }
}

// Teacher Panel Routes
export const TEACHER_ROUTES = {
    // Dashboard
    DASHBOARD: { name: 'TeacherDashboard', path: '/teacher-dashboard' },

    // Assignments
    ASSIGNMENT_LIST: { name: 'TeacherAssignmentList', path: '/teacher-dashboard/assignments' },
    ASSIGNMENT_CREATE: { name: 'TeacherCreateAssignment', path: '/teacher-dashboard/assignments/create' },
    ASSIGNMENT_EDIT: { name: 'TeacherEditAssignment', path: '/teacher-dashboard/assignments/edit' },
    ASSIGNMENT_DELETE: { name: 'TeacherDeleteAssignment', path: '/teacher-dashboard/assignments/delete' },
    SUBMISSIONS: { name: 'TeacherSubmissions', path: '/teacher-dashboard/assignments/submissions' },

    // Attendance
    MARK_ATTENDANCE: { name: 'TeacherMarkAttendance', path: '/teacher-dashboard/attendance/mark' },
    ATTENDANCE_REPORT: { name: 'TeacherAttendanceReport', path: '/teacher-dashboard/attendance/report' },
    STUDENT_ATTENDANCE: { name: 'TeacherStudentAttendance', path: '/teacher-dashboard/attendance/student' },

    // Grades
    GRADE_MANAGEMENT: { name: 'TeacherGradeManagement', path: '/teacher-dashboard/grades' },
    GRADE_STUDENTS: { name: 'TeacherGradeStudents', path: '/teacher-dashboard/grades/students' },
    GRADE_REPORT: { name: 'TeacherGradeReport', path: '/teacher-dashboard/grades/report' },

    // Classes
    CLASS_LIST: { name: 'TeacherClassList', path: '/teacher-dashboard/classes' },
    STUDENT_LIST: { name: 'TeacherStudentList', path: '/teacher-dashboard/students' },
    ANNOUNCEMENTS: { name: 'TeacherAnnouncementList', path: '/teacher-dashboard/classes/announcements' },

    // Schedule
    CLASS_SCHEDULE: { name: 'TeacherClassSchedule', path: '/teacher-dashboard/schedule/class' },
    EXAM_SCHEDULE: { name: 'TeacherExamSchedule', path: '/teacher-dashboard/schedule/exam' },

    // Quizzes
    QUIZ_LIST: { name: 'TeacherQuizList', path: '/teacher-dashboard/quizzes' },
    QUIZ_BUILDER: { name: 'TeacherQuizBuilder', path: '/teacher-dashboard/quizzes/builder' },
    QUIZ_EDIT: { name: 'TeacherQuizEdit', path: '/teacher-dashboard/quizzes/builder' },
    AI_QUIZ_GENERATOR: { name: 'TeacherAiQuizGenerator', path: '/teacher-dashboard/quizzes/ai-generator' },

    // Resources
    MATERIAL_UPLOAD: { name: 'TeacherMaterialUpload', path: '/teacher-dashboard/resources/upload' },
    MATERIAL_DOWNLOAD: { name: 'TeacherMaterialDownload', path: '/teacher-dashboard/resources/download' },

    // Profiles
    STUDENT_PROFILE: { name: 'TeacherStudentProfile', path: '/teacher-dashboard/profiles/student' },
    SUBJECT_PROFILE: { name: 'TeacherSubjectProfile', path: '/teacher-dashboard/profiles/subject' }
}

// Student Panel Routes
export const STUDENT_ROUTES = {
    // Dashboard
    DASHBOARD: { name: 'StudentDashboard', path: '/student-dashboard' },

    // Assignments
    VIEW_ASSIGNMENTS: { name: 'StudentViewAssignments', path: '/student-dashboard/assignments' },
    SUBMIT_ASSIGNMENT: { name: 'StudentSubmitAssignment', path: '/student-dashboard/assignments/submit' },
    SUBMISSION_HISTORY: { name: 'StudentSubmissionHistory', path: '/student-dashboard/assignments/history' },

    // Grades
    MY_GRADES: { name: 'StudentMyGrade', path: '/student-dashboard/grades' },
    GRADE_REPORT: { name: 'StudentGradeReport', path: '/student-dashboard/grades/report' },

    // Attendance
    MY_ATTENDANCE: { name: 'StudentMyAttendance', path: '/student-dashboard/attendance' },

    // Schedule
    CLASS_SCHEDULE: { name: 'StudentClassSchedule', path: '/student-dashboard/schedule/class' },
    EXAM_SCHEDULE: { name: 'StudentExamSchedule', path: '/student-dashboard/schedule/exam' },

    // Resources
    ENROLLED_SUBJECTS: { name: 'StudentEnrolledSubjects', path: '/student-dashboard/resources/subjects' },
    SUBJECT_PROFILE: { name: 'StudentSubjectProfile', path: '/student-dashboard/resources/subjects' },
    COURSE_MATERIAL: { name: 'StudentCourseMaterial', path: '/student-dashboard/resources/material' },
    MATERIAL_PREVIEW: { name: 'StudentMaterialPreview', path: '/student-dashboard/resources/material/preview' },
    LIBRARY_CATALOG: { name: 'StudentLibraryCatalog', path: '/student-dashboard/library' },
    MY_BOOKS: { name: 'StudentMyBooks', path: '/student-dashboard/library/my-books' },

    // Quizzes
    QUIZ_LIST: { name: 'StudentQuizList', path: '/student-dashboard/quizzes' },
    TAKE_QUIZ: { name: 'StudentTakeQuiz', path: '/student-dashboard/quizzes' },

    // Communication
    ANNOUNCEMENTS: { name: 'StudentAnnouncements', path: '/student-dashboard/announcements' }
}

// Helper function to get route with params
export const getRouteWithParams = (route, params = {}) => {
    let path = route.path
    Object.keys(params).forEach(key => {
        path = path.replace(`:${key}`, params[key])
    })
    return path
}

// Helper function to get route with ID
export const getRouteWithId = (route, id) => {
    return `${route.path}/${id}`
}

export default {
    ADMIN_ROUTES,
    TEACHER_ROUTES,
    STUDENT_ROUTES,
    getRouteWithParams,
    getRouteWithId
}
