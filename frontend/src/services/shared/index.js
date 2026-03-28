/**
 * Services Index
 * Centralized exports for all services organized by domain
 */

// Core/Infrastructure
export { default, authAPI } from './core/api'
export { default as api } from './core/api'
export * from './core/apiWrapper'
export * from './core/utils'
export { default as cacheService } from './core/cacheService'

// Academic Domain
export { programService, courseService } from './academic/programService'
export { subjectService } from './academic/subjectService'
export { assignmentService } from './academic/assignmentService'
export { default as sessionService } from './academic/sessionService'
export { default as semesterService } from './academic/semesterService'
export { institutionService } from './academic/institutionService'

// User/Identity Domain
export { studentService } from './users/studentService'
export { teacherService } from './users/teacherService'
export { departmentService } from './users/departmentService'

// Panel Services (Orchestration Layer)
export { default as adminPanelService } from '../admin/adminPanelService'
export { default as teacherPanelService } from '../teacher/teacherPanelService'
export { default as studentPanelService } from '../student/studentPanelService'

// Management Services
export {
    eventService,
    holidayService,
    examService,
    timetableService,
    feeService,
    expenseService,
    accountService,
    libraryBookService,
    bookBorrowingService
} from '../admin/managementService'
