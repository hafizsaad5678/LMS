/**
 * Composable for Student Data Management
 * Provides reusable student data loading and management logic
 */
import { ref } from 'vue'
import teacherPanelService from '@/services/teacher/teacherPanelService'

export function useStudentData() {
    const studentInfo = ref({})
    const loading = ref(false)
    const error = ref(null)

    /**
     * Load student information from classes
     */
    const loadStudentInfo = async (studentId) => {
        loading.value = true
        error.value = null
        try {
            const [foundStudent, detailedStudent] = await Promise.all([
                teacherPanelService.getStudentFromClasses(studentId).catch(() => null),
                teacherPanelService.getStudentDetail(studentId).catch(() => null)
            ])

            const baseStudent = foundStudent || detailedStudent
            if (!baseStudent) return null

            const programName =
                detailedStudent?.program_name ||
                detailedStudent?.program?.name ||
                foundStudent?.program_name ||
                foundStudent?.program?.name ||
                'N/A'

            const departmentName =
                detailedStudent?.department_name ||
                detailedStudent?.program?.department?.name ||
                foundStudent?.department_name ||
                foundStudent?.program?.department?.name ||
                'N/A'

            const normalizedStudent = {
                ...foundStudent,
                ...detailedStudent,
                name: baseStudent.name || baseStudent.full_name || 'Student',
                roll_no: baseStudent.roll_no || baseStudent.enrollment_number || 'N/A',
                program_name: programName,
                department_name: departmentName
            }

            studentInfo.value = normalizedStudent
            return normalizedStudent
        } catch (e) {
            error.value = e.message
            console.error('Error loading student info:', e)
            return null
        } finally {
            loading.value = false
        }
    }

    /**
     * Load all students from teacher's classes
     */
    const loadAllStudents = async () => {
        loading.value = true
        error.value = null
        try {
            const allStudents = await teacherPanelService.getAllStudentsFromClasses()

            // Remove duplicates and sort by name
            const uniqueStudents = []
            const seenStudents = new Set()

            allStudents.forEach(student => {
                if (!seenStudents.has(student.id)) {
                    seenStudents.add(student.id)
                    uniqueStudents.push(student)
                }
            })

            return uniqueStudents.sort((a, b) => a.name.localeCompare(b.name))
        } catch (e) {
            error.value = e.message
            console.error('Error loading students:', e)
            return []
        } finally {
            loading.value = false
        }
    }

    /**
     * Get enrolled subjects for a student
     */
    const getEnrolledSubjects = async (studentId) => {
        const enrolledSubjects = []
        try {
            const classesResponse = await teacherPanelService.getMyClasses()
            const classes = classesResponse.results || classesResponse || []

            for (const cls of classes) {
                try {
                    const studentsResponse = await teacherPanelService.getClassStudents(cls.id)
                    const classStudents = studentsResponse.results || studentsResponse || []

                    const isEnrolled = classStudents.find(s => s.id.toString() === studentId.toString())
                    if (isEnrolled) {
                        enrolledSubjects.push({
                            id: cls.subject_id,
                            name: cls.subject_name,
                            code: cls.subject_code
                        })
                    }
                } catch (err) {
                    // Silent error handling for individual class
                }
            }
        } catch (err) {
            console.error('Error getting enrolled subjects:', err)
        }
        return enrolledSubjects
    }

    return {
        studentInfo,
        loading,
        error,
        loadStudentInfo,
        loadAllStudents,
        getEnrolledSubjects
    }
}
