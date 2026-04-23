/**
 * Student Routes
 * All routes for student dashboard and features
 */
import { STUDENT_ROUTES } from '@/utils/constants/routes'
import { USER_ROLES } from '@/utils/constants/config'

const StudentLayout = () => import('../../layouts/StudentLayout.vue')

export const studentRoutes = {
    path: STUDENT_ROUTES.DASHBOARD.path,
    component: StudentLayout,
    meta: { requiresAuth: true, role: USER_ROLES.STUDENT },
    children: [
        { path: '', name: 'StudentDashboard', component: () => import('../../views/student/dashboard/StudentDashboard.vue') },

        // Account route
        { path: 'account', name: 'StudentMyAccount', component: () => import('../../views/shared/profile/MyAccount.vue') },

        // Assignment routes
        { path: 'assignments', name: 'StudentViewAssignments', component: () => import('../../views/student/assignment/ViewAssignments.vue') },
        { path: 'assignments/submit', name: 'StudentSubmitAssignment', component: () => import('../../views/student/assignment/SubmitAssignment.vue') },
        { path: 'assignments/history', name: 'StudentSubmissionHistory', component: () => import('../../views/student/assignment/SubmissionHistory.vue') },

        // Attendance routes
        { path: 'attendance', name: 'StudentMyAttendance', component: () => import('../../views/student/attendance/MyAttendance.vue') },

        // Grades routes
        { path: 'grades', name: 'StudentMyGrade', component: () => import('../../views/student/grades/MyGrade.vue') },
        { path: 'grades/report', name: 'StudentGradeReport', component: () => import('../../views/student/grades/StudentGradeReport.vue') },
        { path: 'grades/gpa-cgpa-calculator', name: 'StudentGpaCgpaCalculator', component: () => import('../../views/student/grades/GpaCgpaCalculator.vue') },

        // Schedule routes
        { path: 'schedule/class', name: 'StudentClassSchedule', component: () => import('../../views/student/schedule/ClassSchedule.vue') },
        { path: 'schedule/exam', name: 'StudentExamSchedule', component: () => import('../../views/student/schedule/ExamSchedule.vue') },

        // Resources routes
        { path: 'resources/subjects', name: 'StudentEnrolledSubjects', component: () => import('../../views/student/resources/EnrolledSubjects.vue') },
        { path: 'resources/subjects/:id', name: 'StudentSubjectProfile', component: () => import('../../views/student/resources/SubjectProfile.vue') },
        { path: 'resources/material', name: 'StudentCourseMaterial', component: () => import('../../views/student/resources/CourseMaterial.vue') },
        { path: 'resources/material/preview/:id', name: 'StudentMaterialPreview', component: () => import('../../views/student/resources/MaterialPreview.vue') },

        // Communication routes
        { path: 'announcements', name: 'StudentAnnouncements', component: () => import('../../views/student/communication/Announcements.vue') },

        // Quiz routes
        { path: 'quizzes', name: 'StudentQuizList', component: () => import('../../views/student/quizzes/QuizList.vue') },
        { path: 'quizzes/:id', name: 'StudentTakeQuiz', component: () => import('../../views/student/quizzes/TakeQuiz.vue') },

        { path: 'todo', name: 'StudentTodoList', component: () => import('../../views/student/productivity/TodoList.vue') },

        // Library routes
        { path: 'library', name: 'StudentLibraryCatalog', component: () => import('../../views/student/library/LibraryCatalog.vue') },
        { path: 'library/my-books', name: 'StudentMyBooks', component: () => import('../../views/student/library/MyBooks.vue') }
    ]
}
