/**
 * Admin Routes
 * All routes for admin dashboard and management
 */
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { USER_ROLES } from '@/utils/constants/config'
import AdminLayout from '../../layouts/AdminLayout.vue'

export const adminRoutes = {
    path: ADMIN_ROUTES.DASHBOARD.path,
    component: AdminLayout,
    meta: { requiresAuth: true, role: USER_ROLES.ADMIN },
    children: [
        { path: '', name: 'AdminDashboard', component: () => import('../../views/admin/dashboard/AdminDashboard.vue') },

        // Student routes
        { path: 'students', name: 'ListStudent', component: () => import('../../views/admin/student/ListStudent.vue') },
        { path: 'students/add', name: 'AddStudent', component: () => import('../../views/admin/student/AddStudent.vue') },
        { path: 'students/edit/:id?', name: 'EditStudent', component: () => import('../../views/admin/student/EditStudent.vue') },
        { path: 'students/delete/:id?', name: 'DeleteStudent', component: () => import('../../views/admin/student/DeleteStudent.vue') },
        { path: 'students/:id', name: 'StudentProfile', component: () => import('../../views/admin/student/StudentProfile.vue') },

        // Teacher routes
        { path: 'teachers', name: 'ListTeacher', component: () => import('../../views/admin/teacher/ListTeacher.vue') },
        { path: 'teachers/add', name: 'AddTeacher', component: () => import('../../views/admin/teacher/AddTeacher.vue') },
        { path: 'teachers/edit/:id?', name: 'EditTeacher', component: () => import('../../views/admin/teacher/EditTeacher.vue') },
        { path: 'teachers/delete/:id?', name: 'DeleteTeacher', component: () => import('../../views/admin/teacher/DeleteTeacher.vue') },
        { path: 'teachers/:id', name: 'TeacherProfile', component: () => import('../../views/admin/teacher/TeacherProfile.vue') },

        // Institution routes
        { path: 'institution', name: 'ListInstitution', component: () => import('../../views/admin/institution/ListInstitution.vue') },
        { path: 'institution/add', name: 'AddInstitution', component: () => import('../../views/admin/institution/AddInstitution.vue') },
        { path: 'institution/edit/:id?', name: 'EditInstitution', component: () => import('../../views/admin/institution/EditInstitution.vue') },
        { path: 'institution/delete/:id?', name: 'DeleteInstitution', component: () => import('../../views/admin/institution/DeleteInstitution.vue') },
        { path: 'institution/:id', name: 'InstitutionProfile', component: () => import('../../views/admin/institution/InstitutionProfile.vue') },

        // Department routes
        { path: 'departments', name: 'ListDepartment', component: () => import('../../views/admin/department/ListDepartment.vue') },
        { path: 'departments/add', name: 'AddDepartment', component: () => import('../../views/admin/department/AddDepartment.vue') },
        { path: 'departments/edit/:id?', name: 'EditDepartment', component: () => import('../../views/admin/department/EditDepartment.vue') },
        { path: 'departments/delete/:id?', name: 'DeleteDepartment', component: () => import('../../views/admin/department/DeleteDepartment.vue') },
        { path: 'departments/:id', name: 'DepartmentProfile', component: () => import('../../views/admin/department/DepartmentProfile.vue') },

        // Subject routes
        { path: 'subjects', name: 'ListSubject', component: () => import('../../views/admin/subject/ListSubject.vue') },
        { path: 'subjects/add', name: 'AddSubject', component: () => import('../../views/admin/subject/AddSubject.vue') },
        { path: 'subjects/edit/:id?', name: 'EditSubject', component: () => import('../../views/admin/subject/EditSubject.vue') },
        { path: 'subjects/delete/:id?', name: 'DeleteSubject', component: () => import('../../views/admin/subject/DeleteSubject.vue') },
        { path: 'subjects/:id', name: 'SubjectProfile', component: () => import('../../views/admin/subject/SubjectProfile.vue') },

        // Course routes
        { path: 'courses', name: 'ListCourse', component: () => import('../../views/admin/course/ListCourse.vue') },
        { path: 'courses/add', name: 'AddCourse', component: () => import('../../views/admin/course/AddCourse.vue') },
        { path: 'courses/edit/:id?', name: 'EditCourse', component: () => import('../../views/admin/course/EditCourse.vue') },
        { path: 'courses/delete/:id?', name: 'DeleteCourse', component: () => import('../../views/admin/course/DeleteCourse.vue') },
        { path: 'courses/:id', name: 'CourseProfile', component: () => import('../../views/admin/course/CourseProfile.vue') },

        // Semester routes
        { path: 'semesters', name: 'ListSemester', component: () => import('../../views/admin/semester/ListSemester.vue') },
        { path: 'semesters/add', name: 'AddSemester', component: () => import('../../views/admin/semester/AddSemester.vue') },
        { path: 'semesters/edit/:id?', name: 'EditSemester', component: () => import('../../views/admin/semester/EditSemester.vue'), props: true },
        { path: 'semesters/:id', name: 'SemesterProfile', component: () => import('../../views/admin/semester/SemesterProfile.vue'), props: true },

        // Academic Session routes
        { path: 'sessions', name: 'ListSessions', component: () => import('../../views/admin/session/ListSessions.vue') },
        { path: 'sessions/add', name: 'AddSession', component: () => import('../../views/admin/session/AddSession.vue') },
        { path: 'sessions/edit', name: 'EditSessionSelect', component: () => import('../../views/admin/session/EditSession.vue') },
        { path: 'sessions/edit/:id', name: 'EditSession', component: () => import('../../views/admin/session/EditSession.vue'), props: true },
        { path: 'sessions/profile', name: 'SessionProfileSelect', component: () => import('../../views/admin/session/SessionProfile.vue') },
        { path: 'sessions/profile/:id', name: 'SessionProfile', component: () => import('../../views/admin/session/SessionProfile.vue'), props: true },

        // Assignment routes
        { path: 'assignments', name: 'ListAssignment', component: () => import('../../views/admin/assignment/ListAssignment.vue') },
        { path: 'assignments/add', name: 'AddAssignment', component: () => import('../../views/admin/assignment/AddAssignment.vue') },
        { path: 'assignments/edit/:id?', name: 'EditAssignment', component: () => import('../../views/admin/assignment/EditAssignment.vue') },
        { path: 'assignments/delete/:id?', name: 'DeleteAssignment', component: () => import('../../views/admin/assignment/DeleteAssignment.vue') },

        // Management routes
        { path: 'accounts', name: 'Accounts', component: () => import('../../views/admin/management/Accounts.vue') },
        { path: 'fees-collection', name: 'FeesCollection', component: () => import('../../views/admin/management/FeesCollection.vue') },
        { path: 'expenses', name: 'Expenses', component: () => import('../../views/admin/management/Expenses.vue') },

        // Library routes
        { path: 'library', name: 'LibraryDashboard', component: () => import('../../views/admin/library/Library.vue') },
        { path: 'library/books', name: 'LibraryBooks', component: () => import('../../views/admin/library/LibraryBooks.vue') },
        { path: 'library/borrowings', name: 'BookBorrowing', component: () => import('../../views/admin/library/BookBorrowing.vue') },

        // Academic routes
        { path: 'holidays', name: 'Holidays', component: () => import('../../views/admin/academic/Holidays.vue') },
        { path: 'exams', name: 'ExamList', component: () => import('../../views/admin/academic/ExamList.vue') },
        { path: 'events', name: 'Events', component: () => import('../../views/admin/academic/Events.vue') },
        { path: 'timetable', name: 'TimeTable', component: () => import('../../views/admin/academic/TimeTable.vue') }
    ]
}
