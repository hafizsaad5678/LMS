
export const mainNav = [
  { name: 'Departments', href: '/admin-dashboard/departments' },
  { name: 'Courses', href: '/admin-dashboard/courses' },
  { name: 'Expenses', href: '/admin-dashboard/expenses' },
  { name: 'Holidays', href: '/admin-dashboard/holidays' },
  { name: 'Timetable', href: '/admin-dashboard/timetable' }
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
          { name: 'Delete Student', href: '/admin-dashboard/students/delete', icon: '🗑️' },
          { name: 'StudentProfile ', href: '/admin-dashboard/students/profile', icon: '📋' }
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
          { name: 'Delete Teacher', href: '/admin-dashboard/teachers/delete', icon: '🗑️' },
          { name: 'TeacherProfile ', href: '/admin-dashboard/teachers/profile', icon: '📋' }
        ]
      }
    ]
  },
  {
    title: 'Institution',
    items: [
      {
        name: 'Institution',
        href: '/admin-dashboard/institution',
        icon: '🏢',
        submenu: [
          { name: 'Institution List', href: '/admin-dashboard/institution', icon: '📋' },
          { name: 'Add Institution', href: '/admin-dashboard/institution/add', icon: '➕' },
          { name: 'Edit Institution', href: '/admin-dashboard/institution/edit', icon: '✏️' },
          { name: 'Delete Institution', href: '/admin-dashboard/institution/delete', icon: '🗑️' },
          { name: 'InstitutionProfile ', href: '/admin-dashboard/institution/profile', icon: '📋' }
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
          { name: 'Delete Department', href: '/admin-dashboard/departments/delete', icon: '🗑️' },
          { name: 'DepartmentProfile ', href: '/admin-dashboard/departments/profile', icon: '📋' }
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
          { name: 'Delete Subject', href: '/admin-dashboard/subjects/delete', icon: '🗑️' },
          { name: 'SubjectProfile ', href: '/admin-dashboard/subjects/profile', icon: '📋' }
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
          { name: 'Delete Course', href: '/admin-dashboard/courses/delete', icon: '🗑️' },
          { name: 'CourseProfile ', href: '/admin-dashboard/courses/profile', icon: '📋' }
        ]
      }
    ]
  },
  {
    title: 'Semesters',
    items: [
      {
        name: 'Semesters',
        href: '/admin-dashboard/semesters',
        icon: '📅',
        submenu: [
          { name: 'Semester List', href: '/admin-dashboard/semesters', icon: '📋' },
          { name: 'Add Semester', href: '/admin-dashboard/semesters/add', icon: '➕' },
          { name: 'Edit Semester', href: '/admin-dashboard/semesters/edit', icon: '✏️' },
          { name: 'Semester Profile', href: '/admin-dashboard/semesters/profile', icon: '👤' }
        ]
      }
    ]
  },
  {
    title: 'Academic Sessions',
    items: [
      {
        name: 'Sessions',
        href: '/admin-dashboard/sessions',
        icon: '🎓',
        submenu: [
          { name: 'All Sessions', href: '/admin-dashboard/sessions', icon: '📋' },
          { name: 'Create Session', href: '/admin-dashboard/sessions/add', icon: '➕' },
          { name: 'Edit Session', href: '/admin-dashboard/sessions/edit', icon: '✏️' },
          { name: 'Session Profile', href: '/admin-dashboard/sessions/profile', icon: '👤' }
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
      {
        name: 'Library',
        href: '#',
        icon: '📖',
        submenu: [
          { name: 'Overview', href: '/admin-dashboard/library', icon: '📊' },
          { name: 'Books', href: '/admin-dashboard/library/books', icon: '📚' },
          { name: 'Borrowings', href: '/admin-dashboard/library/borrowings', icon: '🔁' }
        ]
      }
    ]
  }
];
