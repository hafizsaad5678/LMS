/**
 * Pagination Composable
 * Reusable pagination logic for list views
 */
import { ref, computed } from 'vue'

/**
 * Create pagination state and methods
 * @param {object} options - Configuration options
 * @returns {object} Pagination state and methods
 */
export const usePagination = (options = {}) => {
    const { pageSize = 10, scrollToTop = true } = options

    const currentPage = ref(1)
    const totalItems = ref(0)

    const totalPages = computed(() => Math.ceil(totalItems.value / pageSize))

    const displayPages = computed(() => {
        const pages = []
        const maxPages = 5
        let startPage = Math.max(1, currentPage.value - Math.floor(maxPages / 2))
        let endPage = Math.min(totalPages.value, startPage + maxPages - 1)

        if (endPage - startPage < maxPages - 1) {
            startPage = Math.max(1, endPage - maxPages + 1)
        }

        for (let i = startPage; i <= endPage; i++) {
            pages.push(i)
        }
        return pages
    })

    /**
     * Paginate array data
     * @param {Array} data - Data to paginate
     * @returns {Array} Paginated data
     */
    const paginate = (data) => {
        if (!Array.isArray(data)) return []
        // Note: totalItems should be updated outside this function 
        // if called from a computed property to avoid Vue warnings/loops.
        const start = (currentPage.value - 1) * pageSize
        const end = start + pageSize
        return data.slice(start, end)
    }

    /**
     * Change page
     * @param {number} page - Page number
     */
    const changePage = (page) => {
        if (page >= 1 && page <= totalPages.value) {
            currentPage.value = page
            if (scrollToTop) {
                window.scrollTo({ top: 0, behavior: 'smooth' })
            }
        }
    }

    /**
     * Go to first page
     */
    const firstPage = () => changePage(1)

    /**
     * Go to last page
     */
    const lastPage = () => changePage(totalPages.value)

    /**
     * Go to next page
     */
    const nextPage = () => changePage(currentPage.value + 1)

    /**
     * Go to previous page
     */
    const prevPage = () => changePage(currentPage.value - 1)

    /**
     * Reset pagination
     */
    const resetPagination = () => {
        currentPage.value = 1
    }

    /**
     * Set total items (for server-side pagination)
     * @param {number} total - Total items count
     */
    const setTotal = (total) => {
        totalItems.value = total
    }

    return {
        // State
        currentPage,
        totalItems,
        totalPages,
        displayPages,
        pageSize,

        // Methods
        paginate,
        changePage,
        firstPage,
        lastPage,
        nextPage,
        prevPage,
        resetPagination,
        setTotal
    }
}

export default usePagination
