export const mainNav = [
  { name: 'My Courses', href: '/student-dashboard/resources/courses' },
  { name: 'Assignments', href: '/student-dashboard/assignments' },
  { name: 'Grades', href: '/student-dashboard/grades' },
  { name: 'Schedule', href: '/student-dashboard/schedule/class' },
  { name: 'Resources', href: '/student-dashboard/resources/material' }
];

export const recentActivities = [
  {
    id: 1,
    message: 'Assignment submitted successfully',
    time: 'Mathematics • 2 hours ago'
  },
  {
    id: 2,
    message: 'Grade posted for Quiz 3',
    time: 'Physics • 4 hours ago'
  },
  {
    id: 3,
    message: 'New course material uploaded',
    time: 'Chemistry • 6 hours ago'
  },
  {
    id: 4,
    message: 'Class schedule updated',
    time: 'Admin • 1 day ago'
  },
  {
    id: 5,
    message: 'Exam schedule announced',
    time: 'Academic Office • 2 days ago'
  }
];

export const sidebarSections = [
  {
    title: 'Dashboard',
    items: [
      { name: 'Dashboard', href: '/student-dashboard', icon: '📊' }
    ]
  },
  {
    title: 'My Courses',
    items: [
      { name: 'Enrolled Courses', href: '/student-dashboard/resources/courses', icon: '📚' },
      { name: 'Course Materials', href: '/student-dashboard/resources/material', icon: '📁' }
    ]
  },
  {
    title: 'Assignments',
    items: [
      {
        name: 'Assignments',
        href: '/student-dashboard/assignments',
        icon: '✏️',
        submenu: [
          { name: 'View Assignments', href: '/student-dashboard/assignments', icon: '📋' },
          { name: 'Submit Assignment', href: '/student-dashboard/assignments/submit', icon: '📤' },
          { name: 'Submission History', href: '/student-dashboard/assignments/history', icon: '📜' }
        ]
      }
    ]
  },
  {
    title: 'Grades',
    items: [
      { name: 'My Grades', href: '/student-dashboard/grades', icon: '📊' },
      { name: 'Grade Report', href: '/student-dashboard/grades/report', icon: '📈' }
    ]
  },
  {
    title: 'Schedule',
    items: [
      { name: 'Class Schedule', href: '/student-dashboard/schedule/class', icon: '📅' },
      { name: 'Exam Schedule', href: '/student-dashboard/schedule/exam', icon: '📝' }
    ]
  },
  {
    title: 'Attendance',
    items: [
      { name: 'My Attendance', href: '/student-dashboard/attendance', icon: '✅' }
    ]
  },
  {
    title: 'Resources',
    items: [
      { name: 'Library', href: '/student-dashboard/resources/library', icon: '📖' },
      { name: 'Downloads', href: '/student-dashboard/resources/download', icon: '💾' }
    ]
  }
];
