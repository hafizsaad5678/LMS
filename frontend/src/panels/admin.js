/**
 * Admin Panel Navigation Configuration
 * Full CRUD access for all entities
 */
import { ADMIN_ROUTES } from '@/utils/constants/routes'

const BASE_PATH = ADMIN_ROUTES.DASHBOARD.path

// Helper to generate standard CRUD submenu for admin
const createCrudSubmenu = (entityPath, entityName, options = {}) => {
  const {
    showDelete = true,
    showProfile = true,
    listIcon = '📋',
    addIcon = '➕',
    editIcon = '✏️',
    deleteIcon = '🗑️',
    profileIcon = '📋'
  } = options

  const submenu = [
    { name: `${entityName} List`, href: `${BASE_PATH}/${entityPath}`, icon: listIcon },
    { name: `Add ${entityName}`, href: `${BASE_PATH}/${entityPath}/add`, icon: addIcon },
    { name: `Edit ${entityName}`, href: `${BASE_PATH}/${entityPath}/edit`, icon: editIcon }
  ]

  if (showDelete) {
    submenu.push({ name: `Delete ${entityName}`, href: `${BASE_PATH}/${entityPath}/delete`, icon: deleteIcon })
  }

  if (showProfile) {
    submenu.push({ name: `${entityName} Profile`, href: `${BASE_PATH}/${entityPath}/profile`, icon: profileIcon })
  }

  return submenu
}

export const mainNav = [
  { name: 'Departments', href: `${BASE_PATH}/departments` },
  { name: 'Courses', href: `${BASE_PATH}/courses` },
  { name: 'Expenses', href: `${BASE_PATH}/expenses` },
  { name: 'Holidays', href: `${BASE_PATH}/holidays` },
  { name: 'Timetable', href: `${BASE_PATH}/timetable` }
]

export const sidebarSections = [
  {
    title: 'Dashboard',
    items: [
      { name: 'Dashboard', href: BASE_PATH, icon: '📊' }
    ]
  },
  {
    title: 'Students',
    items: [
      {
        name: 'Students',
        href: `${BASE_PATH}/students`,
        icon: '👥',
        submenu: createCrudSubmenu('students', 'Student')
      }
    ]
  },
  {
    title: 'Teachers',
    items: [
      {
        name: 'Teachers',
        href: `${BASE_PATH}/teachers`,
        icon: '👨‍🏫',
        submenu: createCrudSubmenu('teachers', 'Teacher')
      }
    ]
  },
  {
    title: 'Institution',
    items: [
      {
        name: 'Institution',
        href: `${BASE_PATH}/institution`,
        icon: '🏢',
        submenu: createCrudSubmenu('institution', 'Institution')
      }
    ]
  },
  {
    title: 'Departments',
    items: [
      {
        name: 'Departments',
        href: `${BASE_PATH}/departments`,
        icon: '🏢',
        submenu: createCrudSubmenu('departments', 'Department')
      }
    ]
  },
  {
    title: 'Subjects',
    items: [
      {
        name: 'Subjects',
        href: `${BASE_PATH}/subjects`,
        icon: '📚',
        submenu: createCrudSubmenu('subjects', 'Subject')
      }
    ]
  },
  {
    title: 'Courses',
    items: [
      {
        name: 'Courses',
        href: `${BASE_PATH}/courses`,
        icon: '📖',
        submenu: createCrudSubmenu('courses', 'Course')
      }
    ]
  },
  {
    title: 'Semesters',
    items: [
      {
        name: 'Semesters',
        href: `${BASE_PATH}/semesters`,
        icon: '📅',
        submenu: createCrudSubmenu('semesters', 'Semester', { showDelete: false })
      }
    ]
  },
  {
    title: 'Academic Sessions',
    items: [
      {
        name: 'Sessions',
        href: `${BASE_PATH}/sessions`,
        icon: '🎓',
        submenu: createCrudSubmenu('sessions', 'Session', { showDelete: false })
      }
    ]
  },
  {
    title: 'Assignments',
    items: [
      {
        name: 'Assignments',
        href: `${BASE_PATH}/assignments`,
        icon: '✏️',
        submenu: createCrudSubmenu('assignments', 'Assignment', { showProfile: false })
      }
    ]
  },
  {
    title: 'Management',
    items: [
      {
        name: 'Management',
        href: '#',
        icon: '⚙️',
        submenu: [
          { name: 'Accounts', href: `${BASE_PATH}/accounts`, icon: '🏦' },
          { name: 'Fees Collection', href: `${BASE_PATH}/fees-collection`, icon: '💰' },
          { name: 'Expenses', href: `${BASE_PATH}/expenses`, icon: '💸' }
        ]
      },
      {
        name: 'Academic',
        href: '#',
        icon: '📚',
        submenu: [
          { name: 'Holidays', href: `${BASE_PATH}/holidays`, icon: '🏖️' },
          { name: 'Exam List', href: `${BASE_PATH}/exams`, icon: '📝' },
          { name: 'Events', href: `${BASE_PATH}/events`, icon: '🎉' },
          { name: 'Time Table', href: `${BASE_PATH}/timetable`, icon: '⏰' }
        ]
      },
      {
        name: 'Library',
        href: '#',
        icon: '📖',
        submenu: [
          { name: 'Overview', href: `${BASE_PATH}/library`, icon: '📊' },
          { name: 'Books', href: `${BASE_PATH}/library/books`, icon: '📚' },
          { name: 'Borrowings', href: `${BASE_PATH}/library/borrowings`, icon: '🔁' }
        ]
      }
    ]
  }
]
