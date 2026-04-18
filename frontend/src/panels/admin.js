/**
 * Admin Panel Navigation Configuration
 * Full CRUD access for all entities
 */
import { ADMIN_ROUTES } from '@/utils/constants/routes'
import { FEATURE_FLAGS } from '@/utils/constants/config'

const BASE_PATH = ADMIN_ROUTES.DASHBOARD.path

// Helper to generate standard CRUD submenu for admin
const createCrudSubmenu = (entityPath, entityName, options = {}) => {
  const {
    showList = true,
    showAdd = true,
    showEdit = true,
    showDelete = true,
    showProfile = true,
    listLabel,
    addLabel,
    editLabel,
    deleteLabel,
    profileLabel,
    extraItems = [],
    listIcon = '📋',
    addIcon = '➕',
    editIcon = '✏️',
    deleteIcon = '🗑️',
    profileIcon = '📋'
  } = options

  const submenu = []

  if (showList) {
    submenu.push({
      name: listLabel || `${entityName} List`,
      href: `${BASE_PATH}/${entityPath}`,
      icon: listIcon
    })
  }

  if (showAdd) {
    submenu.push({
      name: addLabel || `Add ${entityName}`,
      href: `${BASE_PATH}/${entityPath}/add`,
      icon: addIcon
    })
  }

  if (showEdit) {
    submenu.push({
      name: editLabel || `Edit ${entityName}`,
      href: `${BASE_PATH}/${entityPath}/edit`,
      icon: editIcon
    })
  }

  if (showDelete) {
    submenu.push({
      name: deleteLabel || `Delete ${entityName}`,
      href: `${BASE_PATH}/${entityPath}/delete`,
      icon: deleteIcon
    })
  }

  if (showProfile) {
    submenu.push({
      name: profileLabel || `${entityName} Profile`,
      href: `${BASE_PATH}/${entityPath}/profile`,
      icon: profileIcon
    })
  }

  if (Array.isArray(extraItems) && extraItems.length > 0) {
    submenu.push(...extraItems)
  }

  return submenu
}

const createStaticSubmenu = (items = []) => {
  return items.map((item) => ({
    name: item.name,
    href: `${BASE_PATH}/${item.path}`,
    icon: item.icon
  }))
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
    title: 'Academic Sessions',
    items: [
      {
        name: 'Sessions',
        href: `${BASE_PATH}/sessions`,
        icon: '🎓',
        submenu: createCrudSubmenu('sessions', 'Session', {
          showDelete: false,
          profileIcon: '👤',
          extraItems: [
            { name: 'Semester Promotion', href: `${BASE_PATH}/sessions/promotion`, icon: '⏫' }
          ]
        })
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
        submenu: createCrudSubmenu('assignments', 'Assignment', {
          showAdd: FEATURE_FLAGS.ADMIN_ASSIGNMENT_MANAGEMENT,
          showEdit: FEATURE_FLAGS.ADMIN_ASSIGNMENT_MANAGEMENT,
          showDelete: FEATURE_FLAGS.ADMIN_ASSIGNMENT_MANAGEMENT,
          showProfile: false,
          listLabel: 'Assignment List',
          extraItems: [
            { name: 'View Assignment', href: `${BASE_PATH}/assignments/view`, icon: '👁️' }
          ]
        })
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
        submenu: createStaticSubmenu([
          { name: 'Accounts', path: 'accounts', icon: '🏦' },
          { name: 'Fees Collection', path: 'fees-collection', icon: '💰' },
          { name: 'Expenses', path: 'expenses', icon: '💸' }
        ])
      },
      {
        name: 'Academic',
        href: '#',
        icon: '📚',
        submenu: createStaticSubmenu([
          { name: 'Holidays', path: 'holidays', icon: '🏖️' },
          { name: 'Exam List', path: 'exams', icon: '📝' },
          { name: 'Events', path: 'events', icon: '🎉' },
          { name: 'Time Table', path: 'timetable', icon: '⏰' }
        ])
      },
      {
        name: 'Library',
        href: '#',
        icon: '📖',
        submenu: createStaticSubmenu([
          { name: 'Overview', path: 'library', icon: '📊' },
          { name: 'Books', path: 'library/books', icon: '📚' },
          { name: 'Borrowings', path: 'library/borrowings', icon: '🔁' }
        ])
      }
    ]
  }
]
