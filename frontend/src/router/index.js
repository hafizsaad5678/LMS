import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/auth/Login.vue'
import Signup from '../views/auth/Signup.vue'
import ForgotPassword from '../views/auth/ForgotPassword.vue'
import ResetPassword from '../views/auth/ResetPassword.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import StudentLayout from '../layouts/StudentLayout.vue'
import TeacherLayout from '../layouts/TeacherLayout.vue'

// Dashboards
import AdminDashboard from '../views/admin/dashboard/AdminDashboard.vue'
import StudentDashboard from '../views/student/dashboard/StudentDashboard.vue'
import TeacherDashboard from '../views/teacher/dashboard/TeacherDashboard.vue'

// Admin Student views
import ListStudent from '../views/admin/student/ListStudent.vue'
import AddStudent from '../views/admin/student/AddStudent.vue'
import EditStudent from '../views/admin/student/EditStudent.vue'
import DeleteStudent from '../views/admin/student/DeleteStudent.vue'

// Admin Teacher views
import ListTeacher from '../views/admin/teacher/ListTeacher.vue'
import AddTeacher from '../views/admin/teacher/AddTeacher.vue'
import EditTeacher from '../views/admin/teacher/EditTeacher.vue'
import DeleteTeacher from '../views/admin/teacher/DeleteTeacher.vue'

// Admin Department views
import ListDepartment from '../views/admin/department/ListDepartment.vue'
import AddDepartment from '../views/admin/department/AddDepartment.vue'
import EditDepartment from '../views/admin/department/EditDepartment.vue'
import DeleteDepartment from '../views/admin/department/DeleteDepartment.vue'

// Admin Subject views
import ListSubject from '../views/admin/subject/ListSubject.vue'
import AddSubject from '../views/admin/subject/AddSubject.vue'
import EditSubject from '../views/admin/subject/EditSubject.vue'
import DeleteSubject from '../views/admin/subject/DeleteSubject.vue'

// Admin Course views
import ListCourse from '../views/admin/course/ListCourse.vue'
import AddCourse from '../views/admin/course/AddCourse.vue'
import EditCourse from '../views/admin/course/EditCourse.vue'
import DeleteCourse from '../views/admin/course/DeleteCourse.vue'

// Admin Assignment views
import AddAssignment from '../views/admin/assignment/AddAssignment.vue'
import EditAssignment from '../views/admin/assignment/EditAssignment.vue'
import DeleteAssignment from '../views/admin/assignment/DeleteAssignment.vue'
import ListAssignment from '../views/admin/assignment/ListAssignment.vue'

// Admin Management views
import Accounts from '../views/admin/management/Accounts.vue'
import FeesCollection from '../views/admin/management/FeesCollection.vue'
import Expenses from '../views/admin/management/Expenses.vue'
import Salary from '../views/admin/management/Salary.vue'
import Library from '../views/admin/management/Library.vue'

// Admin Academic views
import Holidays from '../views/admin/academic/Holidays.vue'
import ExamList from '../views/admin/academic/ExamList.vue'
import Events from '../views/admin/academic/Events.vue'
import TimeTable from '../views/admin/academic/TimeTable.vue'

// Teacher Class views
import ClassList from '../views/teacher/class/ClassList.vue'
import AddClassMaterial from '../views/teacher/class/AddClassMaterial.vue'
import Announcements from '../views/teacher/class/Announcements.vue'

// Teacher Assignment views
import TeacherAssignmentList from '../views/teacher/assignment/AssignmentList.vue'
import CreateAssignment from '../views/teacher/assignment/CreateAssignment.vue'
import Submissions from '../views/teacher/assignment/Submissions.vue'

// Teacher Attendance views
import MarkAttendance from '../views/teacher/attendance/MarkAttendance.vue'
import AttendanceReport from '../views/teacher/attendance/AttendanceReport.vue'

// Teacher Grades views
import GradeStudents from '../views/teacher/grades/GradeStudents.vue'
import TeacherGradeReport from '../views/teacher/grades/GradeReport.vue'

// Teacher Schedule views
import TeacherClassSchedule from '../views/teacher/schedule/ClassSchedule.vue'
import TeacherExamSchedule from '../views/teacher/schedule/ExamSchedule.vue'

// Teacher Resources views
import MaterialUpload from '../views/teacher/resources/MaterialUpload.vue'
import TeacherMaterialDownload from '../views/teacher/resources/MaterialDownload.vue'

// Student Assignment views
import ViewAssignments from '../views/student/assignment/ViewAssignments.vue'
import SubmitAssignment from '../views/student/assignment/SubmitAssignment.vue'
import SubmissionHistory from '../views/student/assignment/SubmissionHistory.vue'

// Student Attendance views
import MyAttendance from '../views/student/attendance/MyAttendance.vue'

// Student Grades views
import MyGrade from '../views/student/grades/MyGrade.vue'
import StudentGradeReport from '../views/student/grades/StudentGradeReport.vue'

// Student Schedule views
import StudentClassSchedule from '../views/student/schedule/ClassSchedule.vue'
import StudentExamSchedule from '../views/student/schedule/ExamSchedule.vue'

// Student Resources views
import EnrolledCourses from '../views/student/resources/EnrolledCourses.vue'
import CourseMaterial from '../views/student/resources/CourseMaterial.vue'
import StudentMaterialDownload from '../views/student/resources/MaterialDownload.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login, meta: { requiresGuest: true } },
  { path: '/signup', name: 'Signup', component: Signup, meta: { requiresGuest: true } },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword, meta: { requiresGuest: true } },
  { path: '/reset-password/:uidb64/:token', name: 'ResetPassword', component: ResetPassword, meta: { requiresGuest: true } },

  // Admin routes with nested layout
  {
    path: '/admin-dashboard',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'AdminDashboard', component: AdminDashboard },

      // Student routes
      { path: 'students', name: 'ListStudent', component: ListStudent },
      { path: 'students/add', name: 'AddStudent', component: AddStudent },
      { path: 'students/edit', name: 'EditStudent', component: EditStudent },
      { path: 'students/delete', name: 'DeleteStudent', component: DeleteStudent },

      // Teacher routes
      { path: 'teachers', name: 'ListTeacher', component: ListTeacher },
      { path: 'teachers/add', name: 'AddTeacher', component: AddTeacher },
      { path: 'teachers/edit', name: 'EditTeacher', component: EditTeacher },
      { path: 'teachers/delete', name: 'DeleteTeacher', component: DeleteTeacher },

      // Department routes
      { path: 'departments', name: 'ListDepartment', component: ListDepartment },
      { path: 'departments/add', name: 'AddDepartment', component: AddDepartment },
      { path: 'departments/edit', name: 'EditDepartment', component: EditDepartment },
      { path: 'departments/delete', name: 'DeleteDepartment', component: DeleteDepartment },

      // Subject routes
      { path: 'subjects', name: 'ListSubject', component: ListSubject },
      { path: 'subjects/add', name: 'AddSubject', component: AddSubject },
      { path: 'subjects/edit', name: 'EditSubject', component: EditSubject },
      { path: 'subjects/delete', name: 'DeleteSubject', component: DeleteSubject },

      // Course routes
      { path: 'courses', name: 'ListCourse', component: ListCourse },
      { path: 'courses/add', name: 'AddCourse', component: AddCourse },
      { path: 'courses/edit', name: 'EditCourse', component: EditCourse },
      { path: 'courses/delete', name: 'DeleteCourse', component: DeleteCourse },

      // Assignment routes
      { path: 'assignments', name: 'ListAssignment', component: ListAssignment },
      { path: 'assignments/add', name: 'AddAssignment', component: AddAssignment },
      { path: 'assignments/edit', name: 'EditAssignment', component: EditAssignment },
      { path: 'assignments/delete', name: 'DeleteAssignment', component: DeleteAssignment },

      // Management routes
      { path: 'accounts', name: 'Accounts', component: Accounts },
      { path: 'fees-collection', name: 'FeesCollection', component: FeesCollection },
      { path: 'expenses', name: 'Expenses', component: Expenses },
      { path: 'salary', name: 'Salary', component: Salary },
      { path: 'library', name: 'Library', component: Library },

      // Academic routes
      { path: 'holidays', name: 'Holidays', component: Holidays },
      { path: 'exams', name: 'ExamList', component: ExamList },
      { path: 'events', name: 'Events', component: Events },
      { path: 'timetable', name: 'TimeTable', component: TimeTable }
    ]
  },

  // Student routes with nested layout
  {
    path: '/student-dashboard',
    component: StudentLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'StudentDashboard', component: StudentDashboard },

      // Assignment routes
      { path: 'assignments', name: 'StudentViewAssignments', component: ViewAssignments },
      { path: 'assignments/submit', name: 'StudentSubmitAssignment', component: SubmitAssignment },
      { path: 'assignments/history', name: 'StudentSubmissionHistory', component: SubmissionHistory },

      // Attendance routes
      { path: 'attendance', name: 'StudentMyAttendance', component: MyAttendance },

      // Grades routes
      { path: 'grades', name: 'StudentMyGrade', component: MyGrade },
      { path: 'grades/report', name: 'StudentGradeReport', component: StudentGradeReport },

      // Schedule routes
      { path: 'schedule/class', name: 'StudentClassSchedule', component: StudentClassSchedule },
      { path: 'schedule/exam', name: 'StudentExamSchedule', component: StudentExamSchedule },

      // Resources routes
      { path: 'resources/courses', name: 'StudentEnrolledCourses', component: EnrolledCourses },
      { path: 'resources/material', name: 'StudentCourseMaterial', component: CourseMaterial },
      { path: 'resources/download', name: 'StudentMaterialDownload', component: StudentMaterialDownload }
    ]
  },

  // Teacher routes with nested layout
  {
    path: '/teacher-dashboard',
    component: TeacherLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'TeacherDashboard', component: TeacherDashboard },

      // Class routes
      { path: 'classes', name: 'TeacherClassList', component: ClassList },
      { path: 'classes/material', name: 'TeacherAddClassMaterial', component: AddClassMaterial },
      { path: 'classes/announcements', name: 'TeacherAnnouncements', component: Announcements },

      // Assignment routes
      { path: 'assignments', name: 'TeacherAssignmentList', component: TeacherAssignmentList },
      { path: 'assignments/create', name: 'TeacherCreateAssignment', component: CreateAssignment },
      { path: 'assignments/submissions', name: 'TeacherSubmissions', component: Submissions },

      // Attendance routes
      { path: 'attendance/mark', name: 'TeacherMarkAttendance', component: MarkAttendance },
      { path: 'attendance/report', name: 'TeacherAttendanceReport', component: AttendanceReport },

      // Grades routes
      { path: 'grades/students', name: 'TeacherGradeStudents', component: GradeStudents },
      { path: 'grades/report', name: 'TeacherGradeReport', component: TeacherGradeReport },

      // Schedule routes
      { path: 'schedule/class', name: 'TeacherClassSchedule', component: TeacherClassSchedule },
      { path: 'schedule/exam', name: 'TeacherExamSchedule', component: TeacherExamSchedule },

      // Resources routes
      { path: 'resources/upload', name: 'TeacherMaterialUpload', component: MaterialUpload },
      { path: 'resources/download', name: 'TeacherMaterialDownload', component: TeacherMaterialDownload }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Auth guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const userRole = localStorage.getItem('userRole')

  // If user is not authenticated and trying to access protected pages, redirect to login
  if (to.meta.requiresAuth && !token) {
    next('/login')
  }
  // If user is authenticated and trying to access guest-only pages (login, signup, etc), redirect to dashboard
  // This prevents going back to login page after authentication
  else if (to.meta.requiresGuest && token) {
    if (userRole === 'admin') {
      next('/admin-dashboard')
    } else if (userRole === 'teacher') {
      next('/teacher-dashboard')
    } else if (userRole === 'student') {
      next('/student-dashboard')
    } else {
      next()
    }
  }
  // Otherwise allow navigation
  else {
    next()
  }
})

export default router