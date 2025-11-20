export const useSidebarMenu = (role) => {
  const menus = {
    admin: [
      { label: 'Dashboard',   to: '/admin',           icon: '📊' },
      { label: 'Teachers',    to: '/admin/teachers',  icon: '👨‍🏫' },
      { label: 'Students',    to: '/admin/students',  icon: '👥' },
      { label: 'Courses',     to: '/admin/courses',   icon: '📚' },
      { label: 'Logout',      to: '/logout',          icon: '🚪' }
    ],
    teacher: [
      { label: 'Dashboard',   to: '/teacher',         icon: '📊' },
      { label: 'My Courses',  to: '/teacher/courses', icon: '📘' },
      { label: 'Assignments', to: '/teacher/assignments', icon: '📝' },
      { label: 'Logout',      to: '/logout',          icon: '🚪' }
    ],
    student: [
      { label: 'Dashboard',   to: '/student',         icon: '📊' },
      { label: 'My Courses',  to: '/student/courses', icon: '📘' },
      { label: 'Assignments', to: '/student/assignments', icon: '📝' },
      { label: 'Logout',      to: '/logout',          icon: '🚪' }
    ]
  }
  return menus[role] || []
}