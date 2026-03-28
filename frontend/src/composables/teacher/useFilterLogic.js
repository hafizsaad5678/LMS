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

    /**
     * Filter by date range
     */
    const dateRangeFilter = (item) => {
        if (!dateField || filters.value.dateRange === 'all') return true

        const now = new Date()
        const filterDate = new Date()
        const itemDate = new Date(item[dateField])

        switch (filters.value.dateRange) {
            case 'thisWeek':
                filterDate.setDate(now.getDate() - 7)
                break
            case 'lastWeek':
                filterDate.setDate(now.getDate() - 14)
                break
            case 'thisMonth':
                filterDate.setMonth(now.getMonth() - 1)
                break
            case 'lastMonth':
                filterDate.setMonth(now.getMonth() - 2)
                break
            default:
                return true
        }

        return itemDate >= filterDate
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
