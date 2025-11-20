export const mainNav = [
  { name: 'My Classes', href: '/teacher-dashboard/classes' },
  { name: 'Assignments', href: '/teacher-dashboard/assignments' },
  { name: 'Attendance', href: '/teacher-dashboard/attendance/mark' },
  { name: 'Grades', href: '/teacher-dashboard/grades/students' },
  { name: 'Resources', href: '/teacher-dashboard/resources/upload' }
];

export const recentActivities = [
  {
    id: 1,
    message: 'Student submitted assignment',
    time: 'John Smith • 30 minutes ago'
  },
  {
    id: 2,
    message: 'Class attendance marked',
    time: 'Mathematics 101 • 2 hours ago'
  },
  {
    id: 3,
    message: 'New assignment created',
    time: 'Physics Lab • 4 hours ago'
  },
  {
    id: 4,
    message: 'Grades posted for Quiz 2',
    time: 'Chemistry • 1 day ago'
  },
  {
    id: 5,
    message: 'Exam schedule updated',
    time: 'Academic Office • 2 days ago'
  }
];

export const sidebarSections = [
  {
    title: 'Dashboard',
    items: [
      { name: 'Dashboard', href: '/teacher-dashboard', icon: '📊' }
    ]
  },
  {
    title: 'My Classes',
    items: [
      {
        name: 'My Classes',
        href: '/teacher-dashboard/classes',
        icon: '📘',
        submenu: [
          { name: 'Class List', href: '/teacher-dashboard/classes', icon: '📚' },
          { name: 'Add Class Material', href: '/teacher-dashboard/classes/material', icon: '📁' },
          { name: 'Announcements', href: '/teacher-dashboard/classes/announcements', icon: '📢' }
        ]
      }
    ]
  },
  {
    title: 'Assignments',
    items: [
      {
        name: 'Assignments',
        href: '/teacher-dashboard/assignments',
        icon: '📝',
        submenu: [
          { name: 'Assignment List', href: '/teacher-dashboard/assignments', icon: '📋' },
          { name: 'Create Assignment', href: '/teacher-dashboard/assignments/create', icon: '➕' },
          { name: 'Submissions', href: '/teacher-dashboard/assignments/submissions', icon: '📤' }
        ]
      }
    ]
  },
  {
    title: 'Attendance',
    items: [
      {
        name: 'Attendance',
        href: '/teacher-dashboard/attendance/mark',
        icon: '📅',
        submenu: [
          { name: 'Mark Attendance', href: '/teacher-dashboard/attendance/mark', icon: '✏️' },
          { name: 'Attendance Report', href: '/teacher-dashboard/attendance/report', icon: '📊' }
        ]
      }
    ]
  },
  {
    title: 'Grades',
    items: [
      {
        name: 'Grades',
        href: '/teacher-dashboard/grades/students',
        icon: '🏆',
        submenu: [
          { name: 'Grade Students', href: '/teacher-dashboard/grades/students', icon: '📈' },
          { name: 'Grade Report', href: '/teacher-dashboard/grades/report', icon: '📊' }
        ]
      }
    ]
  },
  {
    title: 'Schedule',
    items: [
      { name: 'Class Schedule', href: '/teacher-dashboard/schedule/class', icon: '📅' },
      { name: 'Exam Schedule', href: '/teacher-dashboard/schedule/exam', icon: '📝' }
    ]
  },
  {
    title: 'Resources',
    items: [
      { name: 'Material Upload', href: '/teacher-dashboard/resources/upload', icon: '⬆️' },
      { name: 'Downloads', href: '/teacher-dashboard/resources/download', icon: '⬇️' }
    ]
  }
];
