/**
 * Teacher Routes
 * All routes for teacher dashboard and features
 */
import { TEACHER_ROUTES } from '@/utils/constants/routes'
import { USER_ROLES } from '@/utils/constants/config'

const TeacherLayout = () => import('../../layouts/TeacherLayout.vue')

export const teacherRoutes = {
    path: TEACHER_ROUTES.DASHBOARD.path,
    component: TeacherLayout,
    meta: { requiresAuth: true, role: USER_ROLES.TEACHER },
    children: [
        { path: '', name: 'TeacherDashboard', component: () => import('../../views/teacher/dashboard/TeacherDashboard.vue') },

        // Account route
        { path: 'account', name: 'TeacherMyAccount', component: () => import('../../views/shared/profile/MyAccount.vue') },

        // Class routes
        { path: 'classes', name: 'TeacherClassList', component: () => import('../../views/teacher/class/ClassList.vue') },
        { path: 'classes/announcements', name: 'TeacherAnnouncementList', component: () => import('../../views/teacher/class/AnnouncementList.vue') },

        // Attendance routes
        { path: 'attendance/mark', name: 'TeacherMarkAttendance', component: () => import('../../views/teacher/attendance/MarkAttendance.vue') },
        { path: 'attendance/report', name: 'TeacherAttendanceReport', component: () => import('../../views/teacher/attendance/AttendanceReport.vue') },
        { path: 'attendance/student', name: 'TeacherStudentAttendanceSelect', component: () => import('../../views/teacher/attendance/StudentAttendance.vue') },
        { path: 'attendance/student/:id', name: 'TeacherStudentAttendance', component: () => import('../../views/teacher/attendance/StudentAttendance.vue') },

        // Students routes
        { path: 'students', name: 'TeacherStudentList', component: () => import('../../views/teacher/class/StudentList.vue') },
        { path: 'students/:id', name: 'TeacherStudentProfileById', component: () => import('../../views/teacher/profiles/StudentProfile.vue') },

        // Profile routes
        { path: 'profiles/student', name: 'TeacherStudentProfileSelect', component: () => import('../../views/teacher/profiles/StudentProfile.vue') },
        { path: 'profiles/student/:id', name: 'TeacherStudentProfile', component: () => import('../../views/teacher/profiles/StudentProfile.vue') },
        { path: 'profiles/subject', name: 'TeacherSubjectProfileSelect', component: () => import('../../views/teacher/profiles/SubjectProfile.vue') },
        { path: 'profiles/subject/:id', name: 'TeacherSubjectProfile', component: () => import('../../views/teacher/profiles/SubjectProfile.vue') },

        // Assignment routes
        { path: 'assignments', name: 'TeacherAssignmentList', component: () => import('../../views/teacher/assignment/AssignmentList.vue') },
        { path: 'assignments/create', name: 'TeacherCreateAssignment', component: () => import('../../views/teacher/assignment/CreateAssignment.vue') },
        { path: 'assignments/edit/:id', name: 'TeacherEditAssignment', component: () => import('../../views/teacher/assignment/EditAssignment.vue') },
        { path: 'assignments/delete/:id', name: 'TeacherDeleteAssignment', component: () => import('../../views/teacher/assignment/DeleteAssignment.vue') },
        { path: 'assignments/submissions', name: 'TeacherSubmissions', component: () => import('../../views/teacher/assignment/Submissions.vue') },

        // Grades routes
        { path: 'grades', name: 'TeacherGradeManagement', component: () => import('../../views/teacher/grades/GradeManagement.vue') },
        { path: 'grades/students', name: 'TeacherGradeStudents', component: () => import('../../views/teacher/grades/GradeStudents.vue') },
        { path: 'grades/report', name: 'TeacherGradeReport', component: () => import('../../views/teacher/grades/GradeReport.vue') },

        // Quiz routes
        { path: 'quizzes', name: 'TeacherQuizList', component: () => import('../../views/teacher/quizzes/QuizList.vue') },
        { path: 'quizzes/builder', name: 'TeacherQuizBuilder', component: () => import('../../views/teacher/quizzes/QuizBuilder.vue') },
        { path: 'quizzes/builder/:id', name: 'TeacherQuizEdit', component: () => import('../../views/teacher/quizzes/QuizBuilder.vue') },
        { path: 'quizzes/ai-generator', name: 'TeacherAiQuizGenerator', component: () => import('../../views/teacher/quizzes/AiQuizGenerator.vue') },

        // Schedule routes
        { path: 'schedule/class', name: 'TeacherClassSchedule', component: () => import('../../views/teacher/schedule/ClassSchedule.vue') },
        { path: 'schedule/exam', name: 'TeacherExamSchedule', component: () => import('../../views/teacher/schedule/ExamSchedule.vue') },

        // Resources routes
        { path: 'resources/upload', name: 'TeacherMaterialUpload', component: () => import('../../views/teacher/resources/MaterialUpload.vue') },
        { path: 'resources/download', name: 'TeacherMaterialDownload', component: () => import('../../views/teacher/resources/MaterialDownload.vue') }
    ]
}
