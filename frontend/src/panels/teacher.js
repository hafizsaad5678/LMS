/**
 * Teacher Panel Navigation Configuration
 * Teaching and class management focused
 */
import { TEACHER_ROUTES } from '@/utils/constants/routes'

const BASE_PATH = TEACHER_ROUTES.DASHBOARD.path

// Helper to generate menu items consistently
const createMenuItem = (name, path, icon) => ({
  name,
  href: `${BASE_PATH}${path}`,
  icon
})

// Helper to generate menu items with submenu
const createMenuWithSubmenu = (name, path, icon, submenuItems) => ({
  name,
  href: `${BASE_PATH}${path}`,
  icon,
  submenu: submenuItems.map(item => createMenuItem(item.name, item.path, item.icon))
})

export const mainNav = [
  { name: 'Dashboard', href: BASE_PATH, icon: 'bi bi-speedometer2' },
  { name: 'My Classes', href: `${BASE_PATH}/classes`, icon: 'bi bi-book-half' },
  { name: 'Assignments', href: `${BASE_PATH}/assignments`, icon: 'bi bi-file-text' },
  { name: 'Grades', href: `${BASE_PATH}/grades`, icon: 'bi bi-award' },
  { name: 'Quizzes', href: `${BASE_PATH}/quizzes`, icon: 'bi bi-question-square' },
  { name: 'Attendance', href: `${BASE_PATH}/attendance/mark`, icon: 'bi bi-calendar-check' }
]

export const sidebarSections = [
  // MAIN SECTION
  {
    title: '',
    items: [
      createMenuItem('Dashboard', '', '📊')
    ]
  },

  // ACADEMIC MANAGEMENT
  {
    title: 'ACADEMIC',
    items: [
      createMenuWithSubmenu('My Classes', '/classes', '📘', [
        { name: 'Class List', path: '/classes', icon: '📚' },
        { name: 'Students', path: '/students', icon: '👥' },
        { name: 'Announcements', path: '/classes/announcements', icon: '📢' }
      ]),
      createMenuWithSubmenu('Assignments', '/assignments', '📝', [
        { name: 'All Assignments', path: '/assignments', icon: '📋' },
        { name: 'Create New', path: '/assignments/create', icon: '➕' },
        { name: 'Submissions', path: '/assignments/submissions', icon: '📤' }
      ]),
      createMenuWithSubmenu('Grades', '/grades', '🏆', [
        { name: 'Grade Management', path: '/grades', icon: '📊' },
        { name: 'Grade Students', path: '/grades/students', icon: '📈' },
        { name: 'Grade Report', path: '/grades/report', icon: '📄' }
      ]),
      createMenuWithSubmenu('Attendance', '/attendance/mark', '📅', [
        { name: 'Mark Attendance', path: '/attendance/mark', icon: '✏️' },
        { name: 'Attendance Report', path: '/attendance/report', icon: '📊' },
        { name: 'Student Records', path: '/attendance/student', icon: '👤' }
      ]),
      createMenuWithSubmenu('Online Quizzes', '/quizzes', '❓', [
        { name: 'All Quizzes', path: '/quizzes', icon: '📜' },
        { name: 'Quiz Builder', path: '/quizzes/builder', icon: '🛠️' },
        { name: 'AI Generator', path: '/quizzes/ai-generator', icon: '🤖' }
      ])
    ]
  },

  // SCHEDULE & PLANNING
  {
    title: 'SCHEDULE',
    items: [
      createMenuItem('Class Schedule', '/schedule/class', '📅'),
      createMenuItem('Exam Schedule', '/schedule/exam', '📝')
    ]
  },

  // RESOURCES & MATERIALS
  {
    title: 'RESOURCES',
    items: [
      createMenuItem('Upload Materials', '/resources/upload', '⬆️'),
      createMenuItem('My Materials', '/resources/download', '📁')
    ]
  },

  // PROFILES & INFO
  {
    title: 'PROFILES',
    items: [
      createMenuItem('Student Profiles', '/profiles/student', '👤'),
      createMenuItem('Subject Info', '/profiles/subject', '📖')
    ]
  }
]
