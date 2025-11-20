
export const mainNav = [
  { name: 'Students', href: '/admin-dashboard/students' },
  { name: 'Teachers', href: '/admin-dashboard/teachers' },
  { name: 'Departments', href: '/admin-dashboard/departments' },
  { name: 'Subjects', href: '/admin-dashboard/subjects' },
  { name: 'Courses', href: '/admin-dashboard/courses' }
];

export const recentActivities = [
  {
    id: 1,
    message: 'New student enrolled',
    time: 'John Smith • 2 hours ago'
  },
  {
    id: 2,
    message: 'Teacher added new assignment',
    time: 'Dr. Sarah Wilson • 4 hours ago'
  },
  {
    id: 3,
    message: 'Fee payment received',
    time: 'Michael Brown • 6 hours ago'
  },
  {
    id: 4,
    message: 'New department created',
    time: 'Admin • 1 day ago'
  },
  {
    id: 5,
    message: 'Exam schedule updated',
    time: 'Dr. James Lee • 2 days ago'
  }
];

export const sidebarSections = [
  {
    title: 'Dashboard',
    items: [
      { name: 'Dashboard', href: '/admin-dashboard', icon: '📊' }
    ]
  },
  {
    title: 'Students',
    items: [
      {
        name: 'Students',
        href: '/admin-dashboard/students',
        icon: '👥',
        submenu: [
          { name: 'Student List', href: '/admin-dashboard/students', icon: '📋' },
          { name: 'Add Student', href: '/admin-dashboard/students/add', icon: '➕' },
          { name: 'Edit Student', href: '/admin-dashboard/students/edit', icon: '✏️' },
          { name: 'Delete Student', href: '/admin-dashboard/students/delete', icon: '🗑️' }
        ]
      }
    ]
  },
  {
    title: 'Teachers',
    items: [
      {
        name: 'Teachers',
        href: '/admin-dashboard/teachers',
        icon: '👨‍🏫',
        submenu: [
          { name: 'Teacher List', href: '/admin-dashboard/teachers', icon: '📋' },
          { name: 'Add Teacher', href: '/admin-dashboard/teachers/add', icon: '➕' },
          { name: 'Edit Teacher', href: '/admin-dashboard/teachers/edit', icon: '✏️' },
          { name: 'Delete Teacher', href: '/admin-dashboard/teachers/delete', icon: '🗑️' }
        ]
      }
    ]
  },
  {
    title: 'Departments',
    items: [
      {
        name: 'Departments',
        href: '/admin-dashboard/departments',
        icon: '🏢',
        submenu: [
          { name: 'Department List', href: '/admin-dashboard/departments', icon: '📋' },
          { name: 'Add Department', href: '/admin-dashboard/departments/add', icon: '➕' },
          { name: 'Edit Department', href: '/admin-dashboard/departments/edit', icon: '✏️' },
          { name: 'Delete Department', href: '/admin-dashboard/departments/delete', icon: '🗑️' }
        ]
      }
    ]
  },
  {
    title: 'Subjects',
    items: [
      {
        name: 'Subjects',
        href: '/admin-dashboard/subjects',
        icon: '📚',
        submenu: [
          { name: 'Subject List', href: '/admin-dashboard/subjects', icon: '📋' },
          { name: 'Add Subject', href: '/admin-dashboard/subjects/add', icon: '➕' },
          { name: 'Edit Subject', href: '/admin-dashboard/subjects/edit', icon: '✏️' },
          { name: 'Delete Subject', href: '/admin-dashboard/subjects/delete', icon: '🗑️' }
        ]
      }
    ]
  },
  {
    title: 'Courses',
    items: [
      {
        name: 'Courses',
        href: '/admin-dashboard/courses',
        icon: '📖',
        submenu: [
          { name: 'Course List', href: '/admin-dashboard/courses', icon: '📋' },
          { name: 'Add Course', href: '/admin-dashboard/courses/add', icon: '➕' },
          { name: 'Edit Course', href: '/admin-dashboard/courses/edit', icon: '✏️' },
          { name: 'Delete Course', href: '/admin-dashboard/courses/delete', icon: '🗑️' }
        ]
      }
    ]
  },
  {
    title: 'Assignments',
    items: [
      {
        name: 'Assignments',
        href: '/admin-dashboard/assignments',
        icon: '✏️',
        submenu: [
          { name: 'Assignment List', href: '/admin-dashboard/assignments', icon: '📋' },
          { name: 'Add Assignment', href: '/admin-dashboard/assignments/add', icon: '➕' },
          { name: 'Edit Assignment', href: '/admin-dashboard/assignments/edit', icon: '✏️' },
          { name: 'Delete Assignment', href: '/admin-dashboard/assignments/delete', icon: '🗑️' }
        ]
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
          { name: 'Accounts', href: '/admin-dashboard/accounts', icon: '🏦' },
          { name: 'Fees Collection', href: '/admin-dashboard/fees-collection', icon: '💰' },
          { name: 'Expenses', href: '/admin-dashboard/expenses', icon: '💸' },
          { name: 'Salary', href: '/admin-dashboard/salary', icon: '💵' }
        ]
      },
      {
        name: 'Academic',
        href: '#',
        icon: '📚',
        submenu: [
          { name: 'Holidays', href: '/admin-dashboard/holidays', icon: '🏖️' },
          { name: 'Exam List', href: '/admin-dashboard/exams', icon: '📝' },
          { name: 'Events', href: '/admin-dashboard/events', icon: '🎉' },
          { name: 'Time Table', href: '/admin-dashboard/timetable', icon: '⏰' }
        ]
      },
      { name: 'Library', href: '/admin-dashboard/library', icon: '📖' }
    ]
  }
];
