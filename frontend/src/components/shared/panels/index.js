/**
 * Panels Index
 * Centralized exports for all panel and page template components
 */

// Layout Components
export { default as Navbar } from './layout/Navbar.vue'
export { default as Sidebar } from './layout/Sidebar.vue'
export { default as BasePageTemplate } from './layout/BasePageTemplate.vue'

// Role-Specific Page Templates
export { default as AdminPageTemplate } from './roles/AdminPageTemplate.vue'
export { default as TeacherPageTemplate } from './roles/TeacherPageTemplate.vue'
export { default as StudentPageTemplate } from './roles/StudentPageTemplate.vue'

// AI Chatbot
export { default as StudentAIChatbot } from './StudentAIChatbot.vue'
