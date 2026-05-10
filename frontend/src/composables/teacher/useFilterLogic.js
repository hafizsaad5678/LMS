/**
 * Composable for Common Filter Logic
 * Provides reusable filtering patterns for teacher views
 */
import { ref, computed } from 'vue'
import { smartSearch } from '@/utils'

export function useFilterLogic(items, options = {}) {
    const {
        searchFields = ['name'],
        dateField = null,
        statusField = null,
        subjectField = null
    } = options

    const searchQuery = ref('')
    const filters = ref({
        dateRange: 'all',
        status: '',
        subject: ''
    })

    /**
     * Filter by search query
     */
    const searchFilter = (item) => {
        // Default list of fields to search if none provided (Global Fallback)
        const activeFields = searchFields.length > 0 ? searchFields : ['name', 'subject_name', 'subject_code']
        return smartSearch(item, searchQuery.value, activeFields)
    }

    const parseDate = (value) => {
        if (!value) return null
        const str = String(value)
        const match = str.match(/^(\d{4})-(\d{2})-(\d{2})/)
        if (match) {
            const [, y, m, d] = match
            return new Date(Number(y), Number(m) - 1, Number(d))
        }
        const parsed = new Date(value)
        return Number.isNaN(parsed.getTime()) ? null : parsed
    }

    const startOfDay = (date) => new Date(date.getFullYear(), date.getMonth(), date.getDate())
    const endOfDay = (date) => new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999)
    const startOfWeek = (date) => {
        const start = startOfDay(date)
        const day = start.getDay()
        const diff = (day + 6) % 7
        start.setDate(start.getDate() - diff)
        return start
    }
    const endOfWeek = (date) => {
        const end = startOfWeek(date)
        end.setDate(end.getDate() + 6)
        end.setHours(23, 59, 59, 999)
        return end
    }
    const startOfMonth = (date) => new Date(date.getFullYear(), date.getMonth(), 1)
    const endOfMonth = (date) => new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999)

    /**
     * Filter by date range
     */
    const dateRangeFilter = (item) => {
        if (!dateField || filters.value.dateRange === 'all') return true

        const now = new Date()
        const itemDate = parseDate(item[dateField])
        if (!itemDate) return false

        let start = null
        let end = null

        switch (filters.value.dateRange) {
            case 'thisWeek':
                start = startOfWeek(now)
                end = endOfWeek(now)
                break
            case 'lastWeek': {
                const lastWeek = new Date(now)
                lastWeek.setDate(now.getDate() - 7)
                start = startOfWeek(lastWeek)
                end = endOfWeek(lastWeek)
                break
            }
            case 'thisMonth':
                start = startOfMonth(now)
                end = endOfMonth(now)
                break
            case 'lastMonth': {
                const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1)
                start = startOfMonth(lastMonth)
                end = endOfMonth(lastMonth)
                break
            }
            default:
                return true
        }

        const normalized = startOfDay(itemDate)
        return normalized >= start && normalized <= end
    }

    /**
     * Filter by status
     */
    const statusFilter = (item) => {
        if (!statusField || !filters.value.status) return true
        return item[statusField] === filters.value.status
    }

    /**
     * Filter by subject
     */
    const subjectFilter = (item) => {
        if (!subjectField || !filters.value.subject) return true
        const itemSubject = item[subjectField] || item.subject_id
        return String(itemSubject) === String(filters.value.subject)
    }

    /**
     * Combined filtered items
     */
    const filteredItems = computed(() => {
        return items.value.filter(item =>
            searchFilter(item) &&
            dateRangeFilter(item) &&
            statusFilter(item) &&
            subjectFilter(item)
        )
    })

    /**
     * Reset all filters
     */
    const resetFilters = () => {
        searchQuery.value = ''
        filters.value = {
            dateRange: 'all',
            status: '',
            subject: ''
        }
    }

    return {
        searchQuery,
        filters,
        filteredItems,
        resetFilters
    }
}
