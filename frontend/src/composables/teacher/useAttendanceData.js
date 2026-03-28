/**
 * Composable for Attendance Data Management
 * Provides reusable attendance loading and calculation logic
 */
import { ref, computed } from 'vue'
import { api } from '@/services/shared'
import teacherPanelService from '@/services/teacher/teacherPanelService'

export function useAttendanceData() {
    const attendanceRecords = ref([])
    const loading = ref(false)
    const error = ref(null)

    /**
     * Calculate attendance statistics
     */
    const calculateStats = (records) => {
        const total = records.length
        const present = records.filter(r => r.status === 'present').length
        const absent = records.filter(r => r.status === 'absent').length
        const late = records.filter(r => r.status === 'late').length
        const excused = records.filter(r => r.status === 'excused').length

        return {
            totalClasses: total,
            presentCount: present + late,
            absentCount: absent,
            excusedCount: excused,
            lateCount: late,
            percentage: total > 0 ? Math.round(((present + late) / total) * 100) : 0
        }
    }

    /**
     * Load attendance for a specific student
     */
    const loadStudentAttendance = async (studentId) => {
        loading.value = true
        error.value = null
        try {
            let response
            try {
                response = await api.get(`/students/${studentId}/attendance/`)
            } catch {
                response = await api.get(`/attendance/?student=${studentId}`)
            }

            const rawRecords = response.data.results || response.data || []
            attendanceRecords.value = rawRecords.map(record => ({
                ...record,
                subject_id: record.subject_id || record.subject
            }))

            return attendanceRecords.value
        } catch (err) {
            error.value = err.message
            console.error('Error loading attendance:', err)
            return []
        } finally {
            loading.value = false
        }
    }

    /**
     * Load all attendance records
     */
    const loadAllAttendance = async () => {
        loading.value = true
        error.value = null
        try {
            const response = await teacherPanelService.getAllAttendance()
            attendanceRecords.value = response
            return response
        } catch (err) {
            error.value = err.message
            console.error('Error loading attendance:', err)
            return []
        } finally {
            loading.value = false
        }
    }

    /**
     * Remove duplicate attendance records
     */
    const removeDuplicates = (records) => {
        const uniqueRecords = []
        const seenKeys = new Set()

        records.sort((a, b) => {
            if (a.created_at && b.created_at) {
                return new Date(b.created_at) - new Date(a.created_at)
            }
            return 0
        })

        records.forEach(record => {
            const key = `${record.student}-${record.subject}-${record.session_date}`
            if (!seenKeys.has(key)) {
                seenKeys.add(key)
                uniqueRecords.push(record)
            }
        })

        return uniqueRecords
    }

    return {
        attendanceRecords,
        loading,
        error,
        calculateStats,
        loadStudentAttendance,
        loadAllAttendance,
        removeDuplicates
    }
}
