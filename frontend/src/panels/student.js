/**
 * Student Panel Navigation Configuration
 * Read-only access focused on learning resources
 */
import { STUDENT_ROUTES } from '@/utils/constants/routes'

const BASE_PATH = STUDENT_ROUTES.DASHBOARD.path

// Helper to generate menu items consistently
const createMenuItem = (name, path, icon) => ({
  name,
  href: `${BASE_PATH}${path}`,
  icon
})

export const mainNav = [
  createMenuItem('Quizzes', '/quizzes', null),
  createMenuItem('Attendance', '/attendance', null),
  createMenuItem('Todo List', '/todo', null),
  createMenuItem('Library', '/library', null)

]

export const sidebarSections = [
  {
    title: 'Overview',
    items: [
      createMenuItem('Dashboard', '', '📊')
    ]
  },
  {
    title: 'Academics',
    items: [
      createMenuItem('My Subjects', '/resources/subjects', '📚'),
      createMenuItem('Subject Materials', '/resources/material', '📁'),
      createMenuItem('Online Quizzes', '/quizzes', '🧩'),
      createMenuItem('My Grades', '/grades', '⭐'),
      createMenuItem('Grade Report', '/grades/report', '📈'),
      createMenuItem('CGPA Calculator', '/grades/gpa-cgpa-calculator', '🧮')
    ]
  },
  {
    title: 'Assignments',
    items: [
      createMenuItem('View Assignments', '/assignments', '📋'),
      createMenuItem('Submit Assignment', '/assignments/submit', '📤'),
      createMenuItem('Submission History', '/assignments/history', '📜')
    ]
  },
  {
    title: 'Attendance & Schedule',
    items: [
      createMenuItem('My Attendance', '/attendance', '✅'),
      createMenuItem('Class Schedule', '/schedule/class', '📅'),
      createMenuItem('Exam Schedule', '/schedule/exam', '📝')
    ]
  },
  {
    title: 'Communication',
    items: [
      createMenuItem('Announcements', '/announcements', '📣')
    ]
  },
  {
    title: 'Library',
    items: [
      createMenuItem('Browse Books', '/library', '📖'),
      createMenuItem('My Books', '/library/my-books', '📚')
    ]
  }
]
